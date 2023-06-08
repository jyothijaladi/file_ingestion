resource "aws_cloudwatch_event_rule" "every_5_minutes" {
  name        = "file_ingestion_rule"
  description = "runs at 0th min of 0th hour"

  schedule_expression = "cron(19 20 * * ? *)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.every_5_minutes.name
  target_id = "SendToLambda"
  arn       = aws_lambda_function.copy_landing_raw_lambda_function.arn
  input     = "{\"data_set\":\"movie-lens\"}"
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.copy_landing_raw_lambda_function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_5_minutes.arn
}