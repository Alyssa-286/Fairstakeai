from backend.app.utils.simple_free_rag import get_simple_rag
import json

question = 'What is the notice period for cheque bounce?'
rag = get_simple_rag()
result = rag.query(question)
output = {
    'question': question,
    'answer': result.get('answer'),
    'citations': result.get('citations'),
}
print(json.dumps(output, indent=2)[:4000])
