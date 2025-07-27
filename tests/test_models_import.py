def test_train_result_import():
    from models import TrainResult, train_model

    result = train_model(__import__("pandas").DataFrame())
    assert isinstance(result, TrainResult)
