import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Define Model Structure
class TextClassificationModel(torch.nn.Module):
    def __init__(self, pretrained_model_name, num_classes=10):
        super(TextClassificationModel, self).__init__()
        self.model = AutoModelForSequenceClassification.from_pretrained(pretrained_model_name, num_labels=num_classes)
        
    def forward(self, input_ids, attention_mask):
        return self.model(input_ids, attention_mask=attention_mask)
    

def inference(text):
    # Load the pretrained model
    pretrained_model_name = './kb-albert-char-base-v2'
    model_path = './models/model.pt'
    model = torch.load(model_path)
    model.to('cuda')
    model.eval()

    # Load the tokenizer
    tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name)

    # Tokenize the example text
    inputs = tokenizer(text, padding='max_length', truncation=True, max_length=512, return_tensors='pt')

    # Perform inference
    with torch.no_grad():
        input_ids = inputs['input_ids'].to('cuda')
        attention_mask = inputs['attention_mask'].to('cuda')
        outputs = model(input_ids, attention_mask)
        logits = outputs.logits
        predicted_label = logits.argmax(dim=1).item()

    # Map the predicted label back to the original label name
    labels_mapping = {
        0: '예금',
        1: '주택청약',
        2: '적금',
        3: '펀드',
        4: '대출',
        5: '신탁',
        6: 'ISA',
        7: '보험공제',
        8: '골드',
        9: '외화예금'
    }
    predicted_label_name = labels_mapping[predicted_label]

    return predicted_label_name
    