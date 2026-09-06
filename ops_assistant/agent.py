"""Explicit LangGraph nodes, conditional edges, tool execution and response state."""
import logging
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

logger = logging.getLogger(__name__)

class AgentState(TypedDict, total=False):
    employee_id: str
    message: str
    history: list
    route: str
    arguments: dict
    result: dict
    reply: str
    pending: str | None
    draft: dict | None
    trace: list

def build_graph(store, router):
    def decide(state):
        message = state['message'].strip()
        base = {'result':{}, 'reply':'', 'trace':['decision'], 'arguments':{}}
        if not message or len(message) > 2000:
            return {**base, 'route':'respond', 'reply':'Enter a message of 1–2000 characters.'}
        if message.lower() in {'cancel','reset'}:
            return {**base,'route':'respond','draft':None,'pending':None,'reply':'Pending action cancelled.'}
        if state.get('draft'):
            if message.lower() == 'confirm':
                return {**base, 'route':'ticket_creation','arguments':state['draft']}
            return {**base,'route':'respond','reply':'A draft is awaiting review. Type confirm to create it, or cancel to discard it.'}
        try:
            decision = router.decide(message, state)
            if decision.name in {'answer','clarify'}:
                reply = ('Hello. I can search IT guidance, look up your tickets, or prepare a new ticket.'
                         if decision.name == 'answer' else 'Please describe your IT issue and whether you want guidance, a ticket lookup, or a new ticket.')
                return {**base,'route':'respond','reply':reply}
            return {**base,'route':('prepare' if decision.name == 'ticket_creation' else decision.name),
                    'arguments':decision.arguments.model_dump()}
        except Exception as exc:
            logger.warning('planner_failure type=%s',type(exc).__name__)
            return {**base,'route':'respond','reply':'The planner is unavailable or returned an invalid action. No action was taken. Please retry.'}

    def prepare(state):
        args = state['arguments']
        if not 10 <= len(args['description'].strip()) <= 2000 or not 5 <= len(args['title'].strip()) <= 120:
            return {'pending':'ticket_creation','reply':'Describe the issue in at least 10 characters, including what is failing.',
                    'trace':state['trace']+['validate_missing_information']}
        return {'draft':{'title':args['title'],'description':args['description']},'pending':None,
                'reply':f"Review ticket for {state['employee_id']}:\n\nTitle: {args['title']}\n\nDescription: {args['description']}\n\nType confirm to create, or cancel to discard.",
                'trace':state['trace']+['validate','prepare_draft']}

    def execute(state):
        name, args = state['route'], state['arguments']
        try:
            if name == 'knowledge_search':
                result = {'articles':store.search(args['query'])}
            elif name == 'ticket_lookup':
                result = {'tickets':store.lookup(state['employee_id'],args['query'])}
            elif name == 'ticket_creation' and state.get('draft') and state['message'].strip().lower() == 'confirm':
                result = store.create(state['employee_id'], args['title'], args['description'])
            else:
                raise ValueError('Unapproved action')
            return {'result':result,'draft':None,'pending':None,'trace':state['trace']+[name]}
        except Exception as exc:
            logger.warning('tool_failure tool=%s type=%s',name,type(exc).__name__)
            return {'result':{'error':'The tool could not complete the request. Please retry. Ticket creation retries are deduplicated.'},
                    'trace':state['trace']+[name,'tool_error']}

    def respond(state):
        result = state.get('result',{})
        reply = state.get('reply','')
        if 'error' in result:
            reply = result['error']
        elif 'articles' in result:
            reply = '\n\n'.join(f"Retrieved guidance [{a['id']}] — {a['title']}\n{a['body']}" for a in result['articles']) or 'No matching article was found. Describe the issue differently or ask to create a ticket.'
        elif 'tickets' in result:
            reply = '\n\n'.join(f"{t['id']} — {t['title']}\nStatus: {t['status']}\nCreated: {t['created_at']}" for t in result['tickets']) or 'No matching ticket was found for the selected employee.'
        elif 'ticket' in result:
            ticket = result['ticket']
            prefix = 'Created' if result['created'] else 'An identical active ticket already exists. Reusing'
            reply = f"{prefix} {ticket['id']}.\nTitle: {ticket['title']}\nStatus: {ticket['status']}"
        return {'reply':reply,'history':(state.get('history',[])+[
            {'role':'user','content':state['message']},{'role':'assistant','content':reply}])[-40:],
            'trace':state.get('trace',[])+['response']}

    graph = StateGraph(AgentState)
    for name, node in [('decision',decide),('prepare',prepare),('tools',execute),('response',respond)]:
        graph.add_node(name,node)
    graph.add_edge(START,'decision')
    graph.add_conditional_edges('decision',lambda s:s['route'],{
        'respond':'response','prepare':'prepare','knowledge_search':'tools',
        'ticket_lookup':'tools','ticket_creation':'tools'})
    graph.add_edge('prepare','response')
    graph.add_edge('tools','response')
    graph.add_edge('response',END)
    return graph.compile()

class Assistant:
    def __init__(self, store, router, employee_id):
        store.validate_employee(employee_id)
        self.graph = build_graph(store,router)
        self.employee_id = employee_id
        self.reset()

    def reset(self):
        self.state = {'employee_id':self.employee_id,'history':[],'draft':None,'pending':None}

    def chat(self, message):
        self.state = self.graph.invoke({**self.state,'message':message}, {'recursion_limit':8})
        return self.state
