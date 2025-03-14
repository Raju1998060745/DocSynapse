
# def pullRAG():

     
#     # Retrieve relevant documents
#     retriever = db.as_retriever(
#         search_type="mmr",
#         search_kwargs={"k": 3, "fetch_k": 20, "lambda_mult": 0.5},
#     )
#     relevant_docs = retriever.invoke(text)

#     if not relevant_docs:
#         prompt = prompt_templates.invoke({"text": text})
#         return jsonify({"error": "No relevant documents found"}), 404

#     # Prepare the prompt
#     prompt = prompt_template.invoke({"relevant_docs": relevant_docs[0].page_content, "text": text})

#     # Generate response using Ollama
#     model = ChatGroq(temperature=0, groq_api_key="", model_name="mixtral-8x7b-32768")
#     result = model.invoke(prompt)

