import pytorch_lightning as pl
import wandb
from pytorch_lightning.loggers import WandbLogger
from train import TextClassificationModel, SEED, CustomDataloader
from utils import seed_everything


if __name__ == "__main__":
    # HP Tuning
    # Sweep을 통해 실행될 학습 코드 작성
    sweep_config = {
        "method": "bayes",
        "parameters": {
            "learning_rate": {"values": [1e-5, 7e-6, 5e-6, 3e-6, 1e-6]},
            "max_epoch": {"values": [3, 5, 10]},
            "batch_size": {"values": [8, 16, 32]},
        },
        "metric": {"name": "val_f1", "goal": "maximize"},
    }

    def sweep_train(config=None):
        """
        sweep에서 config로 run
        wandb에 로깅
        """

        with wandb.init(config=config) as run:
            config = wandb.config
            data_path='./data/augmented_data.csv'
            pretrained_model_name='./kb-albert-char-base-v2'
            num_classes = 10
            
            # set seed
            seed_everything(SEED)
            run.name = f"{config.learning_rate}_{config.batch_size}_{config.max_epoch}"
            
            wandb_logger = WandbLogger(project='KB')
            dataloader = CustomDataloader(
                batch_size=config.batch_size, 
                data_path=data_path, 
                pretrained_model_name=pretrained_model_name
                )
            
            model = TextClassificationModel(
                num_classes=num_classes,
                pretrained_model_name=pretrained_model_name,
                learning_rate=config.learning_rate
            )

            trainer = pl.Trainer(
                accelerator="gpu",  # GPU 사용
                max_epochs=config.max_epoch,  # 최대 epoch 수
                logger=wandb_logger,  # wandb logger 사용
                val_check_interval=0.5,  # .5 epoch마다 validation
            )
            trainer.fit(model=model, datamodule=dataloader)  # 모델 학습

    # Sweep 생성
    sweep_id = wandb.sweep(sweep=sweep_config, project='KB')  # config 딕셔너리 추가  # project의 이름 추가
    wandb.agent(sweep_id=sweep_id, function=sweep_train, count=8)  # sweep의 정보를 입력
