import google.generativeai as genai
import cgi

genai.configure(api_key="AIzaSyDBK1BAUc5REhnyxMjgIutWx_P7btKdVs8")
model = genai.GenerativeModel('gemini-1.5-flash')

form = cgi.FieldStorage()
searchterm =  form.getvalue('searchbox')

def ask_compliance_bot(user_query, local_code_text):
    prompt = f"""
    You are an Environmental Compliance Assistant. 
    Use the following legal code to answer the user's question. 
    If the answer isn't in the text, say you don't know.
    ALWAYS cite the specific section number.

    LEGAL CODE:
    {local_code_text}

    USER QUESTION:
    {searchterm}
    """
    response = model.generate_content(prompt)
    return response.text