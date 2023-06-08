resource "aws_sns_topic" "data-ing-updates" {
  name = "data-ing-updates-topic"
}

resource "aws_sns_topic_subscription" "data-ing-updates-target" {
  #topic_arn = "arn:aws:sns:us-east-1:663597504084:data-ing-updates-topic"
  topic_arn = aws_sns_topic.data-ing-updates.arn
  protocol  = "email-json"
  endpoint  = "anil.kittu@gmail.com"
}
