# API Gatewayのリソースを作成
resource "aws_api_gateway_rest_api" "discordbot-apigw" {
  name = "discordbot-apigw"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}


# リソースの作成
resource "aws_api_gateway_resource" "discordbot-apigw" {
  rest_api_id = aws_api_gateway_rest_api.discordbot-apigw.id
  parent_id   = aws_api_gateway_rest_api.discordbot-apigw.root_resource_id
  path_part   = "discord" #リソースのパスを指定してください
}


# メソッドの作成
resource "aws_api_gateway_method" "discordbot-method" {
  rest_api_id      = aws_api_gateway_rest_api.discordbot-apigw.id
  resource_id      = aws_api_gateway_resource.discordbot-apigw.id
  http_method      = "ANY" #HTTPメソッドを指定してください
  authorization    = "NONE"
  api_key_required = false
}

resource "aws_api_gateway_method_response" "discordbot-method-response" {
  rest_api_id = aws_api_gateway_rest_api.discordbot-apigw.id
  resource_id = aws_api_gateway_resource.discordbot-apigw.id
  http_method = aws_api_gateway_method.discordbot-method.http_method
  status_code = "200"
  response_models = {
    "application/json" = "Empty"
  }
  depends_on = [aws_api_gateway_method.discordbot-method]
}

# 統合の作成
resource "aws_api_gateway_integration" "discordbot-integration" {
  rest_api_id             = aws_api_gateway_rest_api.discordbot-apigw.id
  resource_id             = aws_api_gateway_resource.discordbot-apigw.id
  http_method             = aws_api_gateway_method.discordbot-method.http_method
  integration_http_method = "ANY" #HTTPメソッドを指定してください
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.coc-bot-kp-discord.invoke_arn
}

# デプロイメントの作成
resource "aws_api_gateway_deployment" "discord-deployment" {
  rest_api_id = aws_api_gateway_rest_api.discordbot-apigw.id
  depends_on  = [aws_api_gateway_integration.discordbot-integration]
  stage_name  = "dev" #ステージ名を指定してください
}

resource "aws_lambda_permission" "discord-permission" {
  statement_id  = "AllowAPIGatewayInvokeDiscordBot"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.coc-bot-kp-discord.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.discordbot-apigw.execution_arn}/*/*"
}
