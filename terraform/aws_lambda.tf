resource "aws_lambda_function" "coc-bot-kp-discord" {
  filename      = "files/handler.py.zip"
  function_name = "coc-bot-kp-discord"
  role          = aws_iam_role.whl-coc-lambda.arn
  handler       = "handler.run"
  timeout       = 60

  source_code_hash = filebase64sha256("files/handler.py.zip")

  runtime = "python3.9"

  lifecycle {
    create_before_destroy = true
    ignore_changes = [
      last_modified,
      source_code_hash,
      environment,
      memory_size
    ]
  }
}
