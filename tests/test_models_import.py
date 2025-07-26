def test_train_result_import():
    from trading_platform.models import train_model, TrainResult

    result = train_model(__import__("pandas").DataFrame())
    assert isinstance(result, TrainResult)
