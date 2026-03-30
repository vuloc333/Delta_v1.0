from ultralytics import YOLO

model = YOLO("yolo12m.pt")
model.train(
    data="dataset/data.yaml",
    epochs=15,
)