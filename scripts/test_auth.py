from azure.identity import AzureCliCredential

credential = AzureCliCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default")
print("Auth OK, token length:", len(token.token))
