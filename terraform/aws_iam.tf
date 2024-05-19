resource "aws_iam_role" "whl-coc-lambda" {
  name = "whl-coc-lambda"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

data "aws_iam_policy" "AWSLambdaBasicExecutionRole" {
  arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "whl-coc-lambda-basic-role-policy-attach" {
  role       = aws_iam_role.whl-coc-lambda.name
  policy_arn = data.aws_iam_policy.AWSLambdaBasicExecutionRole.arn
}

resource "aws_iam_policy" "whl-coc-lambda-s3-role-policy" {
  name = "s3-coc-pcparams-discord-access-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:*"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:s3:::wheellab-coc-pcparams-discord/*"
      },
      {
        Action = [
          "s3:ListBucket"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:s3:::wheellab-coc-pcparams-discord"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "whl-coc-lambda-s3-role-policy-attachment" {
  policy_arn = aws_iam_policy.whl-coc-lambda-s3-role-policy.arn
  role       = aws_iam_role.whl-coc-lambda.name
}
