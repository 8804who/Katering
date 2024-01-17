import torch
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pytorch_lightning as pl
from sklearn.metrics import f1_score
from pytorch_lightning.loggers import WandbLogger
from sklearn.model_selection import train_test_split
from utils import seed_everything
SEED = 1234

class CustomDataset(Dataset):
    def __init__(self, data, tokenizer, max_length):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __getitem__(self, idx):
        text = self.data.iloc[idx]['summarization']
        label = self.data.iloc[idx]['label']
        encoded = self.tokenizer(text, padding='max_length', truncation=True, max_length=self.max_length, return_tensors='pt')
        return {
            'input_ids': encoded['input_ids'].squeeze(),
            'attention_mask': encoded['attention_mask'].squeeze(),
            'label': label
        }
    
    def __len__(self):
        return len(self.data)


class CustomDataloader(pl.LightningDataModule):
    def __init__(self, batch_size, data_path, pretrained_model_name, max_length=512):
        super().__init__()
        self.batch_size = batch_size
        self.data_path = data_path
        self.max_length = max_length
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name)
    
    def setup(self, stage: str):
        if stage == "fit":
            data = pd.read_csv(self.data_path)
            train_data, valid_data = train_test_split(data, test_size=0.1, shuffle=True, random_state=SEED)
            self.train_dataset = CustomDataset(train_data, self.tokenizer, self.max_length)
            self.valid_dataset = CustomDataset(valid_data, self.tokenizer, self.max_length)
    
    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.batch_size, shuffle=True)

    def val_dataloader(self):
        return DataLoader(self.valid_dataset, batch_size=self.batch_size)
        

class TextClassificationModel(pl.LightningModule):
    def __init__(self, num_classes, pretrained_model_name, learning_rate):
        super(TextClassificationModel, self).__init__()
        self.model = AutoModelForSequenceClassification.from_pretrained(pretrained_model_name, num_labels=num_classes)
        self.loss_fn = torch.nn.CrossEntropyLoss()
        self.lr = learning_rate
    
    
    def forward(self, input_ids, attention_mask):
        return self.model(input_ids, attention_mask=attention_mask)
    
    
    def training_step(self, batch, batch_idx):  # batch_idx는 주로 로깅할 때 배치가 몇 번째로 처리되는지에 사용
        input_ids = batch['input_ids']
        attention_mask = batch['attention_mask']
        label = batch['label']
        
        outputs = self(input_ids, attention_mask)
        logits = outputs.logits  # forward output의 logits 이용해 loss 계산
        loss = self.loss_fn(logits, label)
        self.log('train_loss', loss)
        return loss
    
    
    def validation_step(self, batch, batch_idx):
        input_ids = batch['input_ids']
        attention_mask = batch['attention_mask']
        label = batch['label']

        outputs = self(input_ids, attention_mask)
        logits = outputs.logits
        loss = self.loss_fn(logits, label)
        self.log('val_loss', loss, prog_bar=True)
        
        preds = logits.argmax(dim=1)  # 각 열이 class를 의미, 따라서 dim=1
        f1 = f1_score(label.cpu(), preds.cpu(), average='weighted')
        self.log('val_f1', f1, prog_bar=True)
    
    
    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.lr)  # Learning rate 조정 가능


if __name__ == '__main__':
    # 데이터 경로 및 설정
    seed_everything(seed=SEED)
    data_path = './data/augmented_data.csv'
    data = pd.read_csv(data_path)
    train_data, valid_data = train_test_split(data, test_size=0.1, shuffle=True, random_state=SEED)

    pretrained_model_name = './kb-albert-char-base-v2'  # 또는 다른 pre-trained 모델 지정
    num_classes = 10
    max_length = 512  # 문장 최대 길이

    # wandb setting
    wandb_logger = WandbLogger(
            project='KB',
            name='baseline',
        )

    # 데이터로더 설정
    dataloader = CustomDataloader(batch_size=32, data_path=data_path, pretrained_model_name=pretrained_model_name)

    # 모델 초기화 및 훈련
    model = TextClassificationModel(num_classes, pretrained_model_name, learning_rate=1e-5)

    # PyTorch Lightning Trainer를 통한 모델 훈련
    trainer = pl.Trainer(
        max_epochs=2, 
        accelerator='gpu',
        logger=wandb_logger,
        val_check_interval=0.5
        )

    trainer.fit(model, datamodule=dataloader)
    torch.save(model, "./models/models.pt")
