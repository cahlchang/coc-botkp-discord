# Create DynamoDB table
resource "aws_dynamodb_table" "coc_botkp_discord" {
  name           = "CoCBotKPDiscord"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "PK"
  range_key      = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  attribute {
    name = "GSI1PK"
    type = "S"
  }

  attribute {
    name = "GSI1SK"
    type = "S"
  }

  attribute {
    name = "EntityType"
    type = "S"
  }

  attribute {
    name = "UserID"
    type = "S"
  }

  # Global Secondary Index for querying all items of a specific type
  global_secondary_index {
    name               = "EntityTypeIndex"
    hash_key           = "EntityType"
    range_key          = "SK"
    projection_type    = "ALL"
  }

  # Global Secondary Index for querying user-related data
  global_secondary_index {
    name               = "UserIndex"
    hash_key           = "UserID"
    range_key          = "SK"
    projection_type    = "ALL"
  }

  # Global Secondary Index for flexible queries
  global_secondary_index {
    name               = "GSI1"
    hash_key           = "GSI1PK"
    range_key          = "GSI1SK"
    projection_type    = "ALL"
  }

  tags = {
    Name        = "CoCBotKPDiscord"
    Environment = "Production"
  }
}
