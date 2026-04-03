from ultralytics import YOLO

model = YOLO("yolo12s.pt")
model.train(
    data="dataset/data.yaml",
    epochs=50,
)