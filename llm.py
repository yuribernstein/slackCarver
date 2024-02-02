from typing import Any
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
import json

dumps_dir = './dumps'
ds_dir = './datasets'

class tierOneModel():
    def __init__(self, slack_channel: str) -> None:   
        self.context_file = f"{dumps_dir}/{slack_channel}.json"
        self.context = self.read_context()
        self.tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-large")
        self.model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-large")

    def get_answer(self, user_input, context = None, max_length = 128):
        
        if context == None:
            context = self.context

        input_text = f"prompt: {user_input}\n context: {self.context}"
        input_ids = self.tokenizer(input_text, return_tensors="pt").input_ids

        with torch.no_grad():
            output_ids = self.model.generate(input_ids, max_length=max_length)

        question = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        
        return question

    def read_context(self):
        with open(self.context_file, 'r') as f:
            dump = json.load(f)

        context = ''
        for each in dump:
            context += each['text'] + ' '
            if len(each['code_blocks']) > 0:
                for code_block in each['code_blocks']:
                    context += code_block + ' '
            if len(each['thread']) > 0:
                for thread in each['thread']:
                    context += thread['text'] + ' '
                    if len(thread['code_blocks']) > 0:
                        for code_block in thread['code_blocks']:
                            context += code_block + ' '
        return context
    

    def prepare_dataset(self):
        response = []
        channel_simmary = self.get_answer("summarize the following context. Outline the issue, the solution, and the outcome.")
        for context in channel_simmary.split('.')[:-1]:
            user_input = "generate question that can be answered factually from the given context"
            question = self.get_answer(user_input, context)
            user_input = "generate a factual answer for the given question and context."
            answer = self.get_answer(question, context)
            response.append({"context": context, "question": question, "answer": answer})
        
        with open(f"{ds_dir}/dataset.{self.context_file}.json", 'w') as f:
            json.dump(self.prepare_dataset(), f)

        return response
           