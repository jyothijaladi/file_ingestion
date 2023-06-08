data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "copy_lambda_role" {
  name               = "copy_lambda_role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

data "aws_iam_policy_document" "s3_policy" {
  statement {
    effect = "Allow"


    actions = ["s3:*"]

    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "bucket_policy" {
  name   = "s3_bucket_policy"
  role   = aws_iam_role.copy_lambda_role.name
  policy = data.aws_iam_policy_document.s3_policy.json

}

data "aws_iam_policy_document" "sns_policy" {
  statement {
    effect = "Allow"


    actions = ["sns:*"]

    resources = ["*"]
  }
}


resource "aws_iam_role_policy" "sns_policy" {
  name   = "data-ing-sns-policy"
  role   = aws_iam_role.copy_lambda_role.name
  policy = data.aws_iam_policy_document.sns_policy.json
}


data "archive_file" "lambda" {
  type        = "zip"
  source_file = "..\\src\\copy_landing_raw\\copy-landing-raw.py"
  output_path = "..\\src\\copy_landing_raw\\copy-landing-raw.zip"
}

resource "aws_lambda_function" "copy_landing_raw_lambda_function" {
  # If the file is not in the current working directory you will need to include a
  # path.module in the filename.
  filename      = "..\\src\\copy_landing_raw\\copy-landing-raw.zip"
  function_name = "copy_landing_raw_lambda_function"
  role          = aws_iam_role.copy_lambda_role.arn
  handler       = "copy-landing-raw.handler"

  source_code_hash = data.archive_file.lambda.output_base64sha256

  runtime     = "python3.10"
  timeout     = 900
  memory_size = 128

  environment {
    variables = {
      sns_topic = aws_sns_topic.data-ing-updates.arn
    }
  }

}


