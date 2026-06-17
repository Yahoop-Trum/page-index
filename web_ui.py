# from flask import Flask, request, render_template_string, jsonify, send_file, session
# import os
# import json
# from io import BytesIO
# import yaml
# from types import SimpleNamespace as config
# import litellm
# import time
# from concurrent.futures import ThreadPoolExecutor
# from dotenv import load_dotenv, find_dotenv
# from pageindex import page_index_main
# import traceback
# import logging
# import secrets

# # Load environment variables from .env if present
# env_path = find_dotenv(usecwd=True)
# if not env_path:
#     env_path = os.path.join(os.path.dirname(__file__), 'pageindex', '.env')
# if env_path and os.path.exists(env_path):
#     load_dotenv(env_path)
#     print(f"Loaded environment from: {env_path}")

# # Configure logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# app = Flask(__name__)
# app.secret_key = secrets.token_hex(32)

# # Check for required environment variables
# if not os.getenv('GOOGLE_API_KEY'):
#     print("Warning: GOOGLE_API_KEY environment variable not set. Please set it before running the application.")
#     print("You can set it by running: $env:GOOGLE_API_KEY = 'your_api_key_here' in PowerShell")
#     print("Or create a .env file in the project root with GOOGLE_API_KEY=your_api_key_here")

# UPLOAD_HTML = """
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>PageIndex Document Chatbot</title>
#     <style>
#         * {
#             box-sizing: border-box;
#         }

#         body {
#             margin: 0;
#             font-family: Arial, sans-serif;
#             background: #f4f6f8;
#             color: #222;
#         }

#         .page-wrapper {
#             max-width: 900px;
#             margin: 0 auto;
#             padding: 24px;
#         }

#         .left-panel {
#             background: #ffffff;
#             border-radius: 16px;
#             box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
#             overflow: hidden;
#         }

#         .panel-header {
#             padding: 20px 24px;
#             border-bottom: 1px solid #e9ecef;
#             background: #f8f9fa;
#         }

#         .panel-header h1 {
#             margin: 0 0 8px 0;
#         }

#         .panel-header p {
#             margin: 0;
#             color: #666;
#             font-size: 14px;
#             line-height: 1.5;
#         }

#         .panel-body {
#             padding: 24px;
#         }

#         .upload-form {
#             border: 2px dashed #cfd8dc;
#             border-radius: 12px;
#             padding: 24px;
#             text-align: center;
#             background: #fafbfc;
#         }

#         .upload-form input[type="file"] {
#             width: 100%;
#             padding: 12px;
#             border: 1px solid #ddd;
#             border-radius: 10px;
#             background: #fff;
#             margin-bottom: 16px;
#         }

#         button {
#             background: #007bff;
#             color: #fff;
#             border: none;
#             border-radius: 10px;
#             padding: 12px 20px;
#             cursor: pointer;
#             font-size: 15px;
#             font-weight: 600;
#             transition: background 0.2s ease;
#         }

#         button:hover {
#             background: #0056b3;
#         }

#         .result-box {
#             margin-top: 20px;
#             padding: 16px;
#             border-radius: 12px;
#             background: #f8f9fa;
#         }

#         .error {
#             background: #f8d7da;
#             color: #721c24;
#             border: 1px solid #f5c6cb;
#             border-radius: 10px;
#             padding: 14px;
#             line-height: 1.5;
#         }

#         .success {
#             background: #d4edda;
#             color: #155724;
#             border: 1px solid #c3e6cb;
#             border-radius: 10px;
#             padding: 14px;
#             line-height: 1.5;
#         }

#         .debug-info {
#             margin-top: 12px;
#             padding: 12px;
#             background: #fff3cd;
#             border: 1px solid #ffeeba;
#             border-radius: 10px;
#             color: #856404;
#             white-space: pre-wrap;
#             overflow-x: auto;
#         }

#         .download-link {
#             display: inline-block;
#             margin-top: 14px;
#             color: #007bff;
#             font-weight: 600;
#             text-decoration: none;
#         }

#         .download-link:hover {
#             text-decoration: underline;
#         }

#         /* Floating chatbot icon */
#         #chatbot-icon {
#             position: fixed;
#             bottom: 24px;
#             right: 24px;
#             width: 62px;
#             height: 62px;
#             border-radius: 50%;
#             background: #007bff;
#             color: #fff;
#             display: flex;
#             align-items: center;
#             justify-content: center;
#             font-size: 28px;
#             box-shadow: 0 10px 24px rgba(0, 123, 255, 0.28);
#             cursor: pointer;
#             z-index: 1000;
#             user-select: none;
#         }

#         #chatbot-icon:hover {
#             background: #0056b3;
#         }

#         /* Chat popup */
#         #chatbot-popup {
#             position: fixed;
#             bottom: 98px;
#             right: 24px;
#             width: 380px;
#             max-width: calc(100vw - 32px);
#             height: 560px;
#             background: #ffffff;
#             border-radius: 18px;
#             box-shadow: 0 16px 40px rgba(0, 0, 0, 0.18);
#             display: flex;
#             flex-direction: column;
#             overflow: hidden;
#             z-index: 1000;
#             border: 1px solid #e9ecef;
#         }

#         .hidden {
#             display: none !important;
#         }

#         .chatbot-topbar {
#             background: #007bff;
#             color: #fff;
#             padding: 14px 16px;
#             display: flex;
#             align-items: center;
#             justify-content: space-between;
#         }

#         .chatbot-topbar-title {
#             display: flex;
#             flex-direction: column;
#             gap: 2px;
#         }

#         .chatbot-topbar-title strong {
#             font-size: 15px;
#         }

#         .chatbot-topbar-title span {
#             font-size: 12px;
#             opacity: 0.9;
#         }

#         .chatbot-close {
#             background: transparent;
#             color: #fff;
#             border: none;
#             font-size: 20px;
#             padding: 0;
#             width: 32px;
#             height: 32px;
#             border-radius: 50%;
#             cursor: pointer;
#         }

#         .chatbot-close:hover {
#             background: rgba(255,255,255,0.15);
#         }

#         .chat-window {
#             flex: 1;
#             overflow-y: auto;
#             padding: 16px;
#             background: #f7f7f8;
#             display: flex;
#             flex-direction: column;
#             gap: 12px;
#         }

#         .chat-message {
#             max-width: 82%;
#             padding: 12px 14px;
#             border-radius: 16px;
#             line-height: 1.5;
#             word-wrap: break-word;
#             font-size: 14px;
#         }

#         .chat-message.user {
#             background: #007bff;
#             color: #fff;
#             margin-left: auto;
#             border-bottom-right-radius: 6px;
#         }

#         .chat-message.assistant {
#             background: #e9ecef;
#             color: #222;
#             margin-right: auto;
#             border-bottom-left-radius: 6px;
#         }

#         .chat-message.loading {
#             color: #666;
#             font-style: italic;
#         }

#         .chat-meta {
#             margin-top: 10px;
#             padding-top: 10px;
#             border-top: 1px solid rgba(0, 0, 0, 0.08);
#             font-size: 12px;
#             color: #666;
#         }

#         .empty-note {
#             padding: 12px 14px;
#             border-radius: 10px;
#             background: #fff3cd;
#             color: #856404;
#             border: 1px solid #ffeeba;
#             font-size: 13px;
#         }

#         .chat-input-area {
#             border-top: 1px solid #e9ecef;
#             padding: 12px;
#             background: #fff;
#         }

#         .chat-form {
#             display: flex;
#             gap: 10px;
#             align-items: center;
#         }

#         .chat-form input[type="text"] {
#             flex: 1;
#             padding: 12px 14px;
#             border: 1px solid #ced4da;
#             border-radius: 12px;
#             font-size: 14px;
#             outline: none;
#         }

#         .chat-form input[type="text"]:focus {
#             border-color: #007bff;
#         }

#         .chat-send-btn {
#             min-width: 72px;
#         }

#         @media (max-width: 600px) {
#             .page-wrapper {
#                 padding: 16px;
#             }

#             #chatbot-popup {
#                 right: 12px;
#                 bottom: 86px;
#                 width: calc(100vw - 24px);
#                 height: 70vh;
#             }

#             #chatbot-icon {
#                 right: 12px;
#                 bottom: 12px;
#             }
#         }
#     </style>

#     <script>
#         function toggleChatbot(forceOpen) {
#             const popup = document.getElementById('chatbot-popup');
#             if (!popup) return;

#             if (forceOpen === true) {
#                 popup.classList.remove('hidden');
#                 return;
#             }

#             popup.classList.toggle('hidden');
#         }

#         document.addEventListener('DOMContentLoaded', function () {
#             const qaForm = document.getElementById('qa-form');
#             const chatWindow = document.getElementById('chat-window');
#             const questionInput = document.getElementById('question');
#             const resultPathInput = document.getElementById('result_path');

#             if (!qaForm || !chatWindow || !questionInput || !resultPathInput) {
#                 return;
#             }

#             function scrollToBottom() {
#                 chatWindow.scrollTop = chatWindow.scrollHeight;
#             }

#             function addMessage(role, htmlContent, isHtml = false) {
#                 const bubble = document.createElement('div');
#                 bubble.className = 'chat-message ' + role;

#                 if (isHtml) {
#                     bubble.innerHTML = htmlContent;
#                 } else {
#                     bubble.textContent = htmlContent;
#                 }

#                 chatWindow.appendChild(bubble);
#                 scrollToBottom();
#                 return bubble;
#             }

#             qaForm.addEventListener('submit', function (e) {
#                 e.preventDefault();

#                 const questionText = questionInput.value.trim();
#                 const resultPath = resultPathInput.value.trim();

#                 if (!questionText) {
#                     return;
#                 }

#                 toggleChatbot(true);
#                 addMessage('user', questionText);
#                 questionInput.value = '';

#                 if (!resultPath) {
#                     addMessage(
#                         'assistant',
#                         '<strong>Please upload a PDF first.</strong><br>Once the document is processed, you can chat with it here.',
#                         true
#                     );
#                     return;
#                 }

#                 const loadingBubble = addMessage('assistant loading', 'Thinking...');

#                 const formData = new FormData();
#                 formData.append('question', questionText);
#                 formData.append('result_path', resultPath);

#                 fetch('/ask', {
#                     method: 'POST',
#                     headers: {
#                         'Content-Type': 'application/x-www-form-urlencoded',
#                     },
#                     body: new URLSearchParams(formData)
#                 })
#                 .then(response => response.json())
#                 .then(data => {
#                     loadingBubble.remove();

#                     if (data.error) {
#                         addMessage('assistant', '<strong>Error:</strong> ' + data.error, true);
#                         return;
#                     }

#                     let answerHtml = data.answer || 'No answer generated.';

#                     if (data.source_node) {
#                         const node = data.source_node;
#                         answerHtml += '<div class="chat-meta">';
#                         if (node.node_id) {
#                             answerHtml += '<div><strong>Node ID:</strong> ' + node.node_id + '</div>';
#                         }
#                         if (node.title) {
#                             answerHtml += '<div><strong>Section:</strong> ' + node.title + '</div>';
#                         }
#                         if (node.start_index !== null && node.start_index !== undefined) {
#                             answerHtml += '<div><strong>Pages:</strong> ' + node.start_index;
#                             if (node.end_index !== null && node.end_index !== undefined) {
#                                 answerHtml += ' - ' + node.end_index;
#                             }
#                             answerHtml += '</div>';
#                         }
#                         answerHtml += '</div>';
#                     }

#                     addMessage('assistant', answerHtml, true);
#                 })
#                 .catch(error => {
#                     loadingBubble.remove();
#                     addMessage('assistant', '<strong>Error:</strong> ' + error.message, true);
#                 });
#             });

#             scrollToBottom();
#         });
#     </script>
# </head>
# <body>
#     <div class="page-wrapper">
#         <div class="left-panel">
#             <div class="panel-header">
#                 <h1>PageIndex Document Processor</h1>
#                 <p>Upload one or more PDF files, process them, and use the chatbot icon at the bottom-right to ask questions about the documents.</p>
#             </div>

#             <div class="panel-body">
#                 <form class="upload-form" action="/upload" method="post" enctype="multipart/form-data">
#                     <input type="file" name="file" accept=".pdf" multiple required>
#                     <button type="submit">Process Documents</button>
#                 </form>

#                 {% if result %}
#                 <div class="result-box">
#                     {% if results_list %}
#                         <h3>Processing Results:</h3>
#                         <ul style="list-style: none; padding: 0;">
#                         {% for item in results_list %}
#                             <li style="margin-bottom: 12px; padding: 10px; border-radius: 8px; background: {% if item.error %}#fff3f3{% else %}#f3fff5{% endif %}; border: 1px solid {% if item.error %}#ffcdd2{% else %}#c8e6c9{% endif %};">
#                                 <strong>{{ item.filename }}</strong>: 
#                                 {% if item.error %}
#                                     <span style="color: #c62828;">Error: {{ item.error }}</span>
#                                 {% else %}
#                                     <span style="color: #2e7d32;">{{ item.success }}</span>
#                                     <br>
#                                     <a class="download-link" href="/download?filename={{ item.result_file }}" style="margin-top: 5px;">Download JSON Result</a>
#                                 {% endif %}
#                             </li>
#                         {% endfor %}
#                         </ul>
#                     {% elif error %}
#                         <div class="error">{{ error }}</div>
#                     {% endif %}

#                     {% if debug_info %}
#                         <div class="debug-info"><strong>Debug Info:</strong><br>{{ debug_info }}</div>
#                     {% endif %}
#                 </div>
#                 {% endif %}
#             </div>
#         </div>
#     </div>

#     <div id="chatbot-icon" onclick="toggleChatbot(true)" title="Open chatbot">💬</div>

#     <div id="chatbot-popup" class="hidden">
#         <div class="chatbot-topbar">
#             <div class="chatbot-topbar-title">
#                 <strong>Document Chatbot</strong>
#                 <span>Ask questions about your uploaded PDFs</span>
#             </div>
#             <button type="button" class="chatbot-close" onclick="toggleChatbot()">×</button>
#         </div>

#         <div class="chat-window" id="chat-window">
#             {% if not result_paths %}
#             <div class="empty-note">
#                 Upload one or more PDFs first. After processing, open this chatbot and ask your questions.
#             </div>
#             {% endif %}

#             <div class="chat-message assistant">
#                 Hello! I am ready to answer questions about your uploaded document.
#             </div>
#         </div>

#         <div class="chat-input-area">
#             <form id="qa-form" class="chat-form" action="/ask" method="post">
#                 <input type="hidden" id="result_path" name="result_path" value="{{ result_paths|join(',') if result_paths else '' }}">
#                 <input
#                     type="text"
#                     id="question"
#                     name="question"
#                     placeholder="Ask a question about the documents..."
#                     required
#                 >
#                 <button type="submit" class="chat-send-btn">Send</button>
#             </form>
#         </div>
#     </div>
# </body>
# </html>
# """

# @app.route('/')
# def index():
#     return render_template_string(
#         UPLOAD_HTML,
#         show_qa=True,
#         result_paths=session.get('last_result_paths', [])
#     )

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if not os.getenv('GOOGLE_API_KEY'):
#         error_msg = "GOOGLE_API_KEY environment variable not set. Please set your Google API key."
#         return render_template_string(
#             UPLOAD_HTML,
#             result=True,
#             error=error_msg,
#             show_qa=True,
#             result_paths=session.get('last_result_paths', [])
#         )

#     if 'file' not in request.files:
#         return render_template_string(
#             UPLOAD_HTML,
#             result=True,
#             error="No file uploaded",
#             show_qa=True,
#             result_paths=session.get('last_result_paths', [])
#         )

#     files = request.files.getlist('file')
#     if not files or files[0].filename == '':
#         return render_template_string(
#             UPLOAD_HTML,
#             result=True,
#             error="No files selected",
#             show_qa=True,
#             result_paths=session.get('last_result_paths', [])
#         )

#     results_list = []
#     success_paths = session.get('last_result_paths', [])
    
#     # Load config
#     config_path = os.path.join(os.path.dirname(__file__), 'pageindex', 'config.yaml')
#     with open(config_path, 'r') as f:
#         config_dict = yaml.safe_load(f)
#     opt = config(config_dict)

#     def process_single_file(file):
#         filename = file.filename
#         try:
#             if not filename.lower().endswith('.pdf'):
#                 return {'filename': filename, 'error': "Only PDF files are supported"}
            
#             logger.info(f"Processing file: {filename}")
#             file_bytes = BytesIO(file.read())
            
#             result = page_index_main(file_bytes, opt)
            
#             pdf_name = os.path.splitext(os.path.basename(filename))[0]
#             output_dir = './results'
#             output_file = f'{output_dir}/{pdf_name}_structure.json'
#             os.makedirs(output_dir, exist_ok=True)

#             with open(output_file, 'w', encoding='utf-8') as f:
#                 json.dump(result, f, indent=2)
            
#             return {
#                 'filename': filename,
#                 'success': "✓ Processing completed",
#                 'result_path': output_file,
#                 'result_file': os.path.basename(output_file)
#             }
#         except Exception as e:
#             logger.error(f"Error processing {filename}: {str(e)}")
#             return {'filename': filename, 'error': str(e)}

#     # Process files concurrently
#     with ThreadPoolExecutor(max_workers=5) as executor:
#         batch_results = list(executor.map(process_single_file, files))

#     for res in batch_results:
#         results_list.append(res)
#         if 'result_path' in res:
#             if res['result_path'] not in success_paths:
#                 success_paths.append(res['result_path'])

#     session['last_result_paths'] = success_paths
#     session.modified = True

#     return render_template_string(
#         UPLOAD_HTML,
#         result=True,
#         results_list=results_list,
#         show_qa=True,
#         result_paths=success_paths
#     )

# @app.route('/download')
# def download():
#     filename = request.args.get('filename')
#     if not filename:
#         return "Filename parameter is missing", 400

#     output_dir = './results'
#     result_path = os.path.join(output_dir, filename)
    
#     if not os.path.exists(result_path):
#         return "Result file not found", 404

#     return send_file(
#         result_path,
#         as_attachment=True,
#         download_name=filename,
#         mimetype='application/json'
#     )

# @app.route('/ask', methods=['POST'])
# def ask_question():
#     result_paths_str = request.form.get('result_path') or ",".join(session.get('last_result_paths', []))
#     result_paths = [p.strip() for p in result_paths_str.split(',') if p.strip()]

#     if not result_paths:
#         return jsonify({'error': 'No documents loaded. Please upload PDFs first.'}), 400

#     question = request.form.get('question', '').strip()
#     if not question:
#         return jsonify({'error': 'Please enter a question.'}), 400

#     try:
#         all_structures = []
#         for path in result_paths:
#             if os.path.exists(path):
#                 with open(path, 'r', encoding='utf-8') as f:
#                     all_structures.append(json.load(f))
#             else:
#                 logger.warning(f"File not found: {path}")

#         if not all_structures:
#             return jsonify({'error': 'No valid result files found. Please re-upload documents.'}), 400

#         answer_obj = generate_answer(all_structures, question)
#         return jsonify(answer_obj)

#     except Exception as e:
#         logger.error(f"Error answering question: {e}")
#         logger.error(traceback.format_exc())
#         return jsonify({'error': f'Error processing question: {str(e)}'}), 500

# def generate_answer(document_structures, question):
#     context_parts = []
#     section_map = {}

#     for doc in document_structures:
#         doc_name = doc.get('doc_name', 'Unknown Document')
#         sections = doc.get('structure', [])
        
#         for section in sections:
#             title = section.get('title', '')
#             summary = section.get('summary', '')
#             node_id = section.get('node_id', '')
            
#             context_tag = f"[Doc: {doc_name}, Node: {node_id}]"
#             context_parts.append(f"{context_tag} Section: {title}\nContent: {summary}")
            
#             section_map[context_tag] = {
#                 'node_id': node_id,
#                 'title': title,
#                 'summary': summary,
#                 'start_index': section.get('start_index'),
#                 'end_index': section.get('end_index'),
#                 'doc_name': doc_name
#             }

#     context = "\n\n".join(context_parts)

#     prompt = f'''Based on the following document structures and contents from multiple files, please answer the question: "{question}"

# Document Contents:
# {context}

# IMPORTANT: Include the [Doc: ..., Node: ...] prefix in your response to indicate which document and node(s) contain the answer. 
# Example: "[Doc: report.pdf, Node: 0001] The answer is..."

# Please provide a clear, concise answer based on the provided contents. If the question cannot be answered from the provided documents, say so.'''

#     config_path = os.path.join(os.path.dirname(__file__), 'pageindex', 'config.yaml')
#     with open(config_path, 'r') as f:
#         config_dict = yaml.safe_load(f)

#     opt = config(config_dict)
#     model = getattr(opt, 'model', 'gemini/gemini-pro')

#     if "gemini" in model.lower():
#         answer = _google_completion_simple(model, prompt)
#     else:
#         max_retries = 10
#         messages = [{"role": "user", "content": prompt}]
#         answer = ""

#         for i in range(max_retries):
#             try:
#                 response = litellm.completion(
#                     model=model,
#                     messages=messages,
#                     temperature=0,
#                 )
#                 answer = response.choices[0].message.content
#                 break
#             except Exception as e:
#                 print('************* Retrying *************')
#                 logging.error(f"Error: {e}")
#                 if i < max_retries - 1:
#                     time.sleep(1)
#                 else:
#                     answer = f"Error generating answer: {str(e)}"

#     source_node = None
#     for node_key, node_info in section_map.items():
#         if node_key in answer:
#             source_node = node_info
#             break

#     return {
#         'answer': answer,
#         'source_node': source_node
#     }

# def _google_completion_simple(model, prompt):
#     import google.generativeai as genai

#     api_key = os.getenv("GOOGLE_API_KEY")
#     if not api_key:
#         raise ValueError("GOOGLE_API_KEY environment variable not set")

#     max_retries = 10
#     for i in range(max_retries):
#         try:
#             genai.configure(api_key=api_key)
#             model_obj = genai.GenerativeModel(model.replace('gemini/', ''))
#             chat = model_obj.start_chat()
#             response = chat.send_message(prompt)
#             content = getattr(response, 'text', None)
#             if content is None:
#                 content = str(response)
#             return content
#         except Exception as e:
#             print('************* Retrying *************')
#             logging.error(f"Google API Error: {e}")
#             if i < max_retries - 1:
#                 time.sleep(1)
#             else:
#                 return f"Error generating answer: {str(e)}"

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)

from flask import Flask, request, render_template_string, jsonify, send_file, send_from_directory, session
import os
import json
from io import BytesIO
import yaml
from types import SimpleNamespace as config
import litellm
import time
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv, find_dotenv
from pageindex import page_index_main
import traceback
import logging
import secrets

# Load environment variables from .env if present
env_path = find_dotenv(usecwd=True)
if not env_path:
    env_path = os.path.join(os.path.dirname(__file__), 'pageindex', '.env')
if env_path and os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"Loaded environment from: {env_path}")

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Check for required environment variables
if not os.getenv('GOOGLE_API_KEY'):
    print("Warning: GOOGLE_API_KEY environment variable not set. Please set it before running the application.")
    print("You can set it by running: $env:GOOGLE_API_KEY = 'your_api_key_here' in PowerShell")
    print("Or create a .env file in the project root with GOOGLE_API_KEY=your_api_key_here")

UPLOAD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PageIndex Document Chatbot</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin:0; padding:0; }

        :root{
          --navy:#050A1C;
          --navy2:#080F24;
          --navy3:#0C1530;
          --indigo:#4F46E5;
          --violet:#7C3AED;
          --cyan:#06B6D4;
          --glass:rgba(255,255,255,0.04);
          --glass-border:rgba(255,255,255,0.08);
          --glass-hover:rgba(255,255,255,0.07);
          --text-primary:#F0F4FF;
          --text-secondary:#94A3B8;
          --text-muted:#4B5A7A;
          --gradient-brand:linear-gradient(135deg,#4F46E5,#7C3AED,#06B6D4);
          --gradient-text:linear-gradient(135deg,#818CF8,#C084FC,#22D3EE);
        }

        body {
            font-family: 'Inter', sans-serif;
            background: var(--navy);
            color: var(--text-primary);
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }

        .bg-decor{
          position:fixed;inset:0;z-index:0;pointer-events:none;
          background:radial-gradient(ellipse 70% 50% at 20% -10%,rgba(79,70,229,0.18) 0%,transparent 55%),
                     radial-gradient(ellipse 50% 40% at 90% 30%,rgba(124,58,237,0.12) 0%,transparent 50%),
                     radial-gradient(ellipse 40% 40% at 10% 90%,rgba(6,182,212,0.08) 0%,transparent 50%);
        }
        .bg-grid{
          position:fixed;inset:0;z-index:0;pointer-events:none;
          background-image:linear-gradient(rgba(79,70,229,0.05) 1px,transparent 1px),
                            linear-gradient(90deg,rgba(79,70,229,0.05) 1px,transparent 1px);
          background-size:56px 56px;
          mask-image:radial-gradient(ellipse 90% 70% at 50% 0%,black 0%,transparent 75%);
        }

        /* top bar matching landing page nav */
        .topbar{
          position:relative;z-index:2;
          display:flex;align-items:center;justify-content:space-between;
          padding:0 32px;height:64px;
          background:rgba(5,10,28,0.85);
          backdrop-filter:blur(20px);
          border-bottom:1px solid var(--glass-border);
        }
        .topbar-logo{
          font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:18px;
          background:var(--gradient-text);
          -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
          text-decoration:none;
        }
        .topbar-back{
          display:flex;align-items:center;gap:8px;
          color:var(--text-secondary);text-decoration:none;font-size:14px;font-weight:500;
          transition:color .2s;
        }
        .topbar-back:hover{color:var(--text-primary)}
        .topbar-badge{
          display:inline-flex;align-items:center;gap:7px;
          background:rgba(79,70,229,0.15);border:1px solid rgba(79,70,229,0.35);
          padding:5px 14px;border-radius:100px;
          font-size:12px;font-weight:500;color:#A5B4FC;
        }
        .topbar-badge span{
          width:6px;height:6px;border-radius:50%;background:#818CF8;
          animation:pulse 2s ease-in-out infinite;
        }
        @keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(.8)}}

        .page-wrapper {
            position:relative;z-index:1;
            max-width: 880px;
            margin: 0 auto;
            padding: 48px 24px 80px;
        }

        .left-panel {
            background: var(--glass);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            overflow: hidden;
            backdrop-filter: blur(12px);
            box-shadow: 0 0 60px rgba(79,70,229,0.08);
        }

        .panel-header {
            padding: 32px 36px 28px;
            border-bottom: 1px solid var(--glass-border);
            background: rgba(255,255,255,0.02);
        }

        .panel-header h1 {
            font-family:'Space Grotesk',sans-serif;
            font-size: 26px;
            font-weight: 700;
            letter-spacing: -0.5px;
            margin: 0 0 10px 0;
        }

        .panel-header p {
            margin: 0;
            color: var(--text-secondary);
            font-size: 14px;
            line-height: 1.6;
            max-width: 560px;
        }

        .panel-body {
            padding: 32px 36px 36px;
        }

        .upload-form {
            border: 1.5px dashed rgba(79,70,229,0.35);
            border-radius: 14px;
            padding: 32px 24px;
            text-align: center;
            background: rgba(79,70,229,0.04);
            transition: border-color .2s, background .2s;
        }
        .upload-form:has(input[type="file"]:hover),
        .upload-form:focus-within {
            border-color: rgba(79,70,229,0.6);
            background: rgba(79,70,229,0.07);
        }

        .upload-form input[type="file"] {
            width: 100%;
            padding: 12px;
            border: 1px solid var(--glass-border);
            border-radius: 10px;
            background: rgba(255,255,255,0.04);
            color: var(--text-primary);
            margin-bottom: 18px;
            font-size: 13px;
            font-family: 'Inter', sans-serif;
        }
        .upload-form input[type="file"]::file-selector-button{
            background: rgba(79,70,229,0.2);
            color: var(--text-primary);
            border: 1px solid rgba(79,70,229,0.4);
            border-radius: 7px;
            padding: 7px 14px;
            font-size: 13px;
            font-weight: 500;
            font-family: 'Inter', sans-serif;
            cursor: pointer;
            margin-right: 12px;
            transition: background .2s;
        }
        .upload-form input[type="file"]::file-selector-button:hover{
            background: rgba(79,70,229,0.35);
        }

        button {
            background: var(--gradient-brand);
            color: #fff;
            border: none;
            border-radius: 10px;
            padding: 13px 26px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            transition: transform .2s, box-shadow .2s;
            box-shadow: 0 0 30px rgba(79,70,229,0.25);
        }

        button:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 30px rgba(79,70,229,0.4);
        }

        .result-box {
            margin-top: 24px;
            padding: 4px;
        }

        .result-box h3{
            font-family:'Space Grotesk',sans-serif;
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 14px;
        }

        .error {
            background: rgba(239,68,68,0.1);
            color: #FCA5A5;
            border: 1px solid rgba(239,68,68,0.25);
            border-radius: 12px;
            padding: 16px 18px;
            line-height: 1.5;
            font-size: 14px;
        }

        .success {
            background: rgba(52,211,153,0.1);
            color: #6EE7B7;
            border: 1px solid rgba(52,211,153,0.25);
            border-radius: 12px;
            padding: 16px 18px;
            line-height: 1.5;
        }

        .debug-info {
            margin-top: 14px;
            padding: 14px 16px;
            background: rgba(251,191,36,0.08);
            border: 1px solid rgba(251,191,36,0.25);
            border-radius: 10px;
            color: #FCD34D;
            white-space: pre-wrap;
            overflow-x: auto;
            font-size: 12px;
        }

        .download-link {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            margin-top: 10px;
            color: #22D3EE;
            font-weight: 600;
            font-size: 13px;
            text-decoration: none;
        }

        .download-link:hover {
            text-decoration: underline;
        }

        .result-item{
            margin-bottom: 12px;
            padding: 16px 18px;
            border-radius: 12px;
            list-style: none;
        }
        .result-item.ok{
            background: rgba(52,211,153,0.06);
            border: 1px solid rgba(52,211,153,0.2);
        }
        .result-item.fail{
            background: rgba(239,68,68,0.06);
            border: 1px solid rgba(239,68,68,0.2);
        }
        .result-item strong{ font-size: 14px; font-weight: 600; }
        .result-item .ok-text{ color:#34D399; font-size:13px; }
        .result-item .fail-text{ color:#F87171; font-size:13px; }

        /* Floating chatbot icon */
        #chatbot-icon {
            position: fixed;
            bottom: 28px;
            right: 28px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: var(--gradient-brand);
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            box-shadow: 0 10px 34px rgba(79,70,229,0.45);
            cursor: pointer;
            z-index: 1000;
            user-select: none;
            transition: transform .2s;
        }

        #chatbot-icon:hover {
            transform: scale(1.06);
        }

        /* Chat popup */
        #chatbot-popup {
            position: fixed;
            bottom: 102px;
            right: 28px;
            width: 380px;
            max-width: calc(100vw - 32px);
            height: 560px;
            background: #0A1126;
            border-radius: 18px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            z-index: 1000;
            border: 1px solid var(--glass-border);
            backdrop-filter: blur(20px);
        }

        .hidden {
            display: none !important;
        }

        .chatbot-topbar {
            background: var(--gradient-brand);
            color: #fff;
            padding: 14px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .chatbot-topbar-title {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        .chatbot-topbar-title strong {
            font-family:'Space Grotesk',sans-serif;
            font-size: 15px;
            font-weight: 600;
        }

        .chatbot-topbar-title span {
            font-size: 12px;
            opacity: 0.9;
        }

        .chatbot-close {
            background: rgba(255,255,255,0.12);
            color: #fff;
            border: none;
            font-size: 18px;
            padding: 0;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            cursor: pointer;
            box-shadow: none;
        }

        .chatbot-close:hover {
            background: rgba(255,255,255,0.22);
            transform: none;
        }

        .chat-window {
            flex: 1;
            overflow-y: auto;
            padding: 18px;
            background: var(--navy2);
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .chat-message {
            max-width: 84%;
            padding: 12px 14px;
            border-radius: 14px;
            line-height: 1.5;
            word-wrap: break-word;
            font-size: 13.5px;
        }

        .chat-message.user {
            background: var(--gradient-brand);
            color: #fff;
            margin-left: auto;
            border-bottom-right-radius: 5px;
        }

        .chat-message.assistant {
            background: rgba(255,255,255,0.06);
            border: 1px solid var(--glass-border);
            color: var(--text-primary);
            margin-right: auto;
            border-bottom-left-radius: 5px;
        }

        .chat-message.loading {
            color: var(--text-secondary);
            font-style: italic;
        }

        .chat-meta {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid rgba(255,255,255,0.08);
            font-size: 12px;
            color: var(--text-secondary);
        }
        .chat-meta strong{ color: var(--text-primary); font-weight: 600; }

        .empty-note {
            padding: 12px 14px;
            border-radius: 10px;
            background: rgba(251,191,36,0.08);
            color: #FCD34D;
            border: 1px solid rgba(251,191,36,0.25);
            font-size: 12.5px;
        }

        .chat-input-area {
            border-top: 1px solid var(--glass-border);
            padding: 14px;
            background: #0A1126;
        }

        .chat-form {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .chat-form input[type="text"] {
            flex: 1;
            padding: 12px 14px;
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            font-size: 13.5px;
            outline: none;
            background: rgba(255,255,255,0.05);
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
        }
        .chat-form input[type="text"]::placeholder{ color: var(--text-muted); }

        .chat-form input[type="text"]:focus {
            border-color: rgba(79,70,229,0.5);
            background: rgba(79,70,229,0.06);
        }

        .chat-send-btn {
            min-width: 68px;
            padding: 11px 16px;
            font-size: 13px;
        }

        @media (max-width: 600px) {
            .page-wrapper {
                padding: 28px 16px 80px;
            }
            .panel-header, .panel-body{
                padding: 24px;
            }

            #chatbot-popup {
                right: 12px;
                bottom: 88px;
                width: calc(100vw - 24px);
                height: 70vh;
            }

            #chatbot-icon {
                right: 14px;
                bottom: 14px;
            }
        }
    </style>

    <script>
        function toggleChatbot(forceOpen) {
            const popup = document.getElementById('chatbot-popup');
            if (!popup) return;

            if (forceOpen === true) {
                popup.classList.remove('hidden');
                return;
            }

            popup.classList.toggle('hidden');
        }

        document.addEventListener('DOMContentLoaded', function () {
            const qaForm = document.getElementById('qa-form');
            const chatWindow = document.getElementById('chat-window');
            const questionInput = document.getElementById('question');
            const resultPathInput = document.getElementById('result_path');

            if (!qaForm || !chatWindow || !questionInput || !resultPathInput) {
                return;
            }

            function scrollToBottom() {
                chatWindow.scrollTop = chatWindow.scrollHeight;
            }

            function addMessage(role, htmlContent, isHtml = false) {
                const bubble = document.createElement('div');
                bubble.className = 'chat-message ' + role;

                if (isHtml) {
                    bubble.innerHTML = htmlContent;
                } else {
                    bubble.textContent = htmlContent;
                }

                chatWindow.appendChild(bubble);
                scrollToBottom();
                return bubble;
            }

            qaForm.addEventListener('submit', function (e) {
                e.preventDefault();

                const questionText = questionInput.value.trim();
                const resultPath = resultPathInput.value.trim();

                if (!questionText) {
                    return;
                }

                toggleChatbot(true);
                addMessage('user', questionText);
                questionInput.value = '';

                if (!resultPath) {
                    addMessage(
                        'assistant',
                        '<strong>Please upload a PDF first.</strong><br>Once the document is processed, you can chat with it here.',
                        true
                    );
                    return;
                }

                const loadingBubble = addMessage('assistant loading', 'Thinking...');

                const formData = new FormData();
                formData.append('question', questionText);
                formData.append('result_path', resultPath);

                fetch('/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams(formData)
                })
                .then(response => response.json())
                .then(data => {
                    loadingBubble.remove();

                    if (data.error) {
                        addMessage('assistant', '<strong>Error:</strong> ' + data.error, true);
                        return;
                    }

                    let answerHtml = data.answer || 'No answer generated.';

                    if (data.source_node) {
                        const node = data.source_node;
                        answerHtml += '<div class="chat-meta">';
                        if (node.node_id) {
                            answerHtml += '<div><strong>Node ID:</strong> ' + node.node_id + '</div>';
                        }
                        if (node.title) {
                            answerHtml += '<div><strong>Section:</strong> ' + node.title + '</div>';
                        }
                        if (node.start_index !== null && node.start_index !== undefined) {
                            answerHtml += '<div><strong>Pages:</strong> ' + node.start_index;
                            if (node.end_index !== null && node.end_index !== undefined) {
                                answerHtml += ' - ' + node.end_index;
                            }
                            answerHtml += '</div>';
                        }
                        answerHtml += '</div>';
                    }

                    addMessage('assistant', answerHtml, true);
                })
                .catch(error => {
                    loadingBubble.remove();
                    addMessage('assistant', '<strong>Error:</strong> ' + error.message, true);
                });
            });

            scrollToBottom();
        });
    </script>
</head>
<body>
    <div class="bg-decor"></div>
    <div class="bg-grid"></div>

    <div class="topbar">
        <a href="/" class="topbar-logo">PageIndex</a>
        <div class="topbar-badge"><span></span> Live demo &middot; vectorless RAG</div>
        <a href="/" class="topbar-back">&larr; Back to overview</a>
    </div>

    <div class="page-wrapper">
        <div class="left-panel">
            <div class="panel-header">
                <h1>Document processor</h1>
                <p>Upload one or more PDF files, process them, and use the chatbot icon at the bottom-right to ask questions about the documents.</p>
            </div>

            <div class="panel-body">
                <form class="upload-form" action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" accept=".pdf" multiple required>
                    <button type="submit">Process documents</button>
                </form>

                {% if result %}
                <div class="result-box">
                    {% if results_list %}
                        <h3>Processing results</h3>
                        <ul style="list-style: none; padding: 0;">
                        {% for item in results_list %}
                            <li class="result-item {% if item.error %}fail{% else %}ok{% endif %}">
                                <strong>{{ item.filename }}</strong>:
                                {% if item.error %}
                                    <span class="fail-text">Error: {{ item.error }}</span>
                                {% else %}
                                    <span class="ok-text">{{ item.success }}</span>
                                    <br>
                                    <a class="download-link" href="/download?filename={{ item.result_file }}">&darr; Download JSON result</a>
                                {% endif %}
                            </li>
                        {% endfor %}
                        </ul>
                    {% elif error %}
                        <div class="error">{{ error }}</div>
                    {% endif %}

                    {% if debug_info %}
                        <div class="debug-info"><strong>Debug info:</strong><br>{{ debug_info }}</div>
                    {% endif %}
                </div>
                {% endif %}
            </div>
        </div>
    </div>

    <div id="chatbot-icon" onclick="toggleChatbot(true)" title="Open chatbot">&#128172;</div>

    <div id="chatbot-popup" class="hidden">
        <div class="chatbot-topbar">
            <div class="chatbot-topbar-title">
                <strong>Document chatbot</strong>
                <span>Ask questions about your uploaded PDFs</span>
            </div>
            <button type="button" class="chatbot-close" onclick="toggleChatbot()">&times;</button>
        </div>

        <div class="chat-window" id="chat-window">
            {% if not result_paths %}
            <div class="empty-note">
                Upload one or more PDFs first. After processing, open this chatbot and ask your questions.
            </div>
            {% endif %}

            <div class="chat-message assistant">
                Hello! I am ready to answer questions about your uploaded document.
            </div>
        </div>

        <div class="chat-input-area">
            <form id="qa-form" class="chat-form" action="/ask" method="post">
                <input type="hidden" id="result_path" name="result_path" value="{{ result_paths|join(',') if result_paths else '' }}">
                <input
                    type="text"
                    id="question"
                    name="question"
                    placeholder="Ask a question about the documents..."
                    required
                >
                <button type="submit" class="chat-send-btn">Send</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def landing():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'pageindex-landing.html')

@app.route('/app')
def index():
    return render_template_string(
        UPLOAD_HTML,
        show_qa=True,
        result_paths=session.get('last_result_paths', [])
    )

@app.route('/upload', methods=['POST'])
def upload_file():
    if not os.getenv('GOOGLE_API_KEY'):
        error_msg = "GOOGLE_API_KEY environment variable not set. Please set your Google API key."
        return render_template_string(
            UPLOAD_HTML,
            result=True,
            error=error_msg,
            show_qa=True,
            result_paths=session.get('last_result_paths', [])
        )

    if 'file' not in request.files:
        return render_template_string(
            UPLOAD_HTML,
            result=True,
            error="No file uploaded",
            show_qa=True,
            result_paths=session.get('last_result_paths', [])
        )

    files = request.files.getlist('file')
    if not files or files[0].filename == '':
        return render_template_string(
            UPLOAD_HTML,
            result=True,
            error="No files selected",
            show_qa=True,
            result_paths=session.get('last_result_paths', [])
        )

    results_list = []
    success_paths = session.get('last_result_paths', [])
    
    # Load config
    config_path = os.path.join(os.path.dirname(__file__), 'pageindex', 'config.yaml')
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    opt = config(config_dict)

    def process_single_file(file):
        filename = file.filename
        try:
            if not filename.lower().endswith('.pdf'):
                return {'filename': filename, 'error': "Only PDF files are supported"}
            
            logger.info(f"Processing file: {filename}")
            file_bytes = BytesIO(file.read())
            
            result = page_index_main(file_bytes, opt)
            
            pdf_name = os.path.splitext(os.path.basename(filename))[0]
            output_dir = './results'
            output_file = f'{output_dir}/{pdf_name}_structure.json'
            os.makedirs(output_dir, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            
            return {
                'filename': filename,
                'success': "✓ Processing completed",
                'result_path': output_file,
                'result_file': os.path.basename(output_file)
            }
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            return {'filename': filename, 'error': str(e)}

    # Process files concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        batch_results = list(executor.map(process_single_file, files))

    for res in batch_results:
        results_list.append(res)
        if 'result_path' in res:
            if res['result_path'] not in success_paths:
                success_paths.append(res['result_path'])

    session['last_result_paths'] = success_paths
    session.modified = True

    return render_template_string(
        UPLOAD_HTML,
        result=True,
        results_list=results_list,
        show_qa=True,
        result_paths=success_paths
    )

@app.route('/download')
def download():
    filename = request.args.get('filename')
    if not filename:
        return "Filename parameter is missing", 400

    output_dir = './results'
    result_path = os.path.join(output_dir, filename)
    
    if not os.path.exists(result_path):
        return "Result file not found", 404

    return send_file(
        result_path,
        as_attachment=True,
        download_name=filename,
        mimetype='application/json'
    )

@app.route('/ask', methods=['POST'])
def ask_question():
    result_paths_str = request.form.get('result_path') or ",".join(session.get('last_result_paths', []))
    result_paths = [p.strip() for p in result_paths_str.split(',') if p.strip()]

    if not result_paths:
        return jsonify({'error': 'No documents loaded. Please upload PDFs first.'}), 400

    question = request.form.get('question', '').strip()
    if not question:
        return jsonify({'error': 'Please enter a question.'}), 400

    try:
        all_structures = []
        for path in result_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    all_structures.append(json.load(f))
            else:
                logger.warning(f"File not found: {path}")

        if not all_structures:
            return jsonify({'error': 'No valid result files found. Please re-upload documents.'}), 400

        answer_obj = generate_answer(all_structures, question)
        return jsonify(answer_obj)

    except Exception as e:
        logger.error(f"Error answering question: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Error processing question: {str(e)}'}), 500

def generate_answer(document_structures, question):
    context_parts = []
    section_map = {}

    for doc in document_structures:
        doc_name = doc.get('doc_name', 'Unknown Document')
        sections = doc.get('structure', [])
        
        for section in sections:
            title = section.get('title', '')
            summary = section.get('summary', '')
            node_id = section.get('node_id', '')
            
            context_tag = f"[Doc: {doc_name}, Node: {node_id}]"
            context_parts.append(f"{context_tag} Section: {title}\nContent: {summary}")
            
            section_map[context_tag] = {
                'node_id': node_id,
                'title': title,
                'summary': summary,
                'start_index': section.get('start_index'),
                'end_index': section.get('end_index'),
                'doc_name': doc_name
            }

    context = "\n\n".join(context_parts)

    prompt = f'''Based on the following document structures and contents from multiple files, please answer the question: "{question}"

Document Contents:
{context}

IMPORTANT: Include the [Doc: ..., Node: ...] prefix in your response to indicate which document and node(s) contain the answer. 
Example: "[Doc: report.pdf, Node: 0001] The answer is..."

Please provide a clear, concise answer based on the provided contents. If the question cannot be answered from the provided documents, say so.'''

    config_path = os.path.join(os.path.dirname(__file__), 'pageindex', 'config.yaml')
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)

    opt = config(config_dict)
    model = getattr(opt, 'model', 'gemini/gemini-pro')

    if "gemini" in model.lower():
        answer = _google_completion_simple(model, prompt)
    else:
        max_retries = 10
        messages = [{"role": "user", "content": prompt}]
        answer = ""

        for i in range(max_retries):
            try:
                response = litellm.completion(
                    model=model,
                    messages=messages,
                    temperature=0,
                )
                answer = response.choices[0].message.content
                break
            except Exception as e:
                print('************* Retrying *************')
                logging.error(f"Error: {e}")
                if i < max_retries - 1:
                    time.sleep(1)
                else:
                    answer = f"Error generating answer: {str(e)}"

    source_node = None
    for node_key, node_info in section_map.items():
        if node_key in answer:
            source_node = node_info
            break

    return {
        'answer': answer,
        'source_node': source_node
    }

def _google_completion_simple(model, prompt):
    import google.generativeai as genai

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")

    max_retries = 10
    for i in range(max_retries):
        try:
            genai.configure(api_key=api_key)
            model_obj = genai.GenerativeModel(model.replace('gemini/', ''))
            chat = model_obj.start_chat()
            response = chat.send_message(prompt)
            content = getattr(response, 'text', None)
            if content is None:
                content = str(response)
            return content
        except Exception as e:
            print('************* Retrying *************')
            logging.error(f"Google API Error: {e}")
            if i < max_retries - 1:
                time.sleep(1)
            else:
                return f"Error generating answer: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)