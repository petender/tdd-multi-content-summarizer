# 🎯 Multi-Source AI Content Summarizer

A versatile, multi-language content summarization application powered by Azure OpenAI GPT-4. Transform articles, documents, text, and videos into concise, actionable summaries in 10+ languages.

## ✨ Features

### 4 Content Input Methods
1. **📄 Web Articles** - Summarize blog posts, news articles, and web pages by URL
2. **📝 Direct Text** - Paste any text content for instant analysis  
3. **📋 PDF Documents** - Upload and extract insights from PDF files
4. **🎥 YouTube Videos** - Get summaries from video transcripts (local use)

### 🌐 Multi-Language Support
Generate summaries in:
- English 🇬🇧
- Spanish 🇪🇸
- French 🇫🇷
- German 🇩🇪
- Japanese 🇯🇵
- Chinese 🇨🇳
- Hindi 🇮🇳
- Portuguese 🇵🇹
- Russian 🇷🇺
- Arabic 🇸🇦

### 🤖 AI-Powered Analysis
Each summary includes:
- **Executive Summary** - 2-3 sentence overview
- **Key Topics** - Main themes and subjects
- **Main Takeaways** - 3-5 actionable insights
- **Action Items** - Recommended next steps

## 🏗️ Architecture

### Azure Services
- **Azure OpenAI** - GPT-4 for intelligent summarization and translation
- **Azure Functions** - Serverless API endpoints (Python)
- **Azure Cosmos DB** - Document storage for summaries
- **Azure Static Web Apps** - Next.js frontend hosting

### Tech Stack
- **Backend**: Python 3.11, Azure Functions, FastAPI
- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **AI**: Azure OpenAI GPT-4, BeautifulSoup, PyPDF2, newspaper3k
- **Database**: Azure Cosmos DB (NoSQL)

## 🚀 Deployment

### Prerequisites
- Azure subscription
- Azure Developer CLI (`azd`) - [Install here](https://aka.ms/azd-install)
- Python 3.11+
- Node.js 18+

### Quick Start

1. **Clone and setup:**
```bash
git clone <your-repo>
cd azd-demo-live
```

2. **Login to Azure:**
```bash
azd auth login
```

3. **Deploy to Azure:**
```bash
azd up
```

This single command will:
- Provision all Azure resources (OpenAI, Cosmos DB, Functions, Static Web App)
- Deploy the Function App (API)
- Deploy the Static Web App (UI)
- Configure connections automatically

4. **Access your app:**
The deployment will output URLs for your application:
- **Web App**: `https://app-<random-id>.azurewebsites.net/`
- **API**: `https://func-<random-id>.azurewebsites.net/api`

### Local Development

1. **Setup Azure resources first (one-time):**
```bash
azd auth login
azd up
```

2. **Backend (Azure Functions):**
```bash
cd api
cp local.settings.json.template local.settings.json
# Edit local.settings.json with your Azure credentials
pip install -r requirements.txt
func start
```

3. **Frontend (Next.js):**
```bash
cd web
npm install
npm run dev
```

Access locally at `http://localhost:3000`

### Subsequent Deployments

After making code changes, simply run:
```bash
azd deploy
```

The deployment process automatically:
- Installs Python dependencies
- Installs Node.js dependencies
- Builds the Next.js app
- Packages both services
- Deploys to Azure

No manual build steps required!

## 📁 Project Structure

```
azd-demo-live/
├── api/                      # Azure Functions (Python)
│   ├── function_app.py      # API endpoints
│   ├── requirements.txt      # Python dependencies
│   └── shared/              # Shared modules
│       ├── openai_client.py # GPT-4 integration
│       ├── web_scraper.py   # Article extraction
│       ├── pdf_processor.py  # PDF text extraction
│       ├── text_processor.py # Text validation
│       └── video_processor.py # YouTube transcripts
│
├── web/                      # Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx           # Landing page
│   │   │   ├── article/page.tsx   # Web article UI
│   │   │   ├── text/page.tsx      # Text input UI
│   │   │   ├── pdf/page.tsx       # PDF upload UI
│   │   │   └── youtube/page.tsx   # YouTube UI
│   │   └── components/
│   │       ├── Navigation.tsx       # Shared navigation
│   │       ├── LanguageSelector.tsx # Language dropdown
│   │       └── SummaryDisplay.tsx   # Result display
│   └── package.json
│
└── infra/                    # Bicep infrastructure
    └── main.bicep           # Azure resource definitions
```

## 🔌 API Endpoints

### POST /api/summarize-article
Summarize a web article
```json
{
  "articleUrl": "https://example.com/article",
  "userId": "user123",
  "language": "English"
}
```

### POST /api/summarize-text
Summarize direct text input
```json
{
  "text": "Your content here...",
  "userId": "user123",
  "language": "French"
}
```

### POST /api/summarize-pdf
Summarize a PDF document
```json
{
  "pdfBase64": "base64_encoded_pdf_data",
  "filename": "document.pdf",
  "userId": "user123",
  "language": "Spanish"
}
```

### POST /api/summarize (YouTube)
Summarize a YouTube video
```json
{
  "videoUrl": "https://youtube.com/watch?v=...",
  "userId": "user123",
  "language": "English"
}
```

## ⚙️ Configuration

### Environment Variables

**Azure Functions** (api/local.settings.json for local dev):
```json
{
  "IsEncrypted": false,
  "Values": {
    "AZURE_OPENAI_ENDPOINT": "https://your-openai.openai.azure.com",
    "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4o",
    "COSMOS_ENDPOINT": "https://your-cosmos.documents.azure.com:443/",
    "COSMOS_DATABASE_NAME": "videodb",
    "COSMOS_CONTAINER_NAME": "summaries"
  }
}
```

**Next.js** (web/.env.local for local dev):
```
NEXT_PUBLIC_API_URL=https://your-function-app.azurewebsites.net/api
```

## 🎯 Use Cases

### For Businesses
- Summarize meeting transcripts in multiple languages
- Extract key points from lengthy reports
- Analyze competitor blog posts
- Process customer feedback documents

### For Researchers
- Quickly digest research papers
- Extract insights from multiple sources
- Translate and summarize foreign language content

### For Content Creators
- Repurpose long-form content
- Generate social media snippets
- Create multilingual content summaries

## 🔒 Security

- **Authentication**: Azure Active Directory integration
- **RBAC**: Cosmos DB role-based access control
- **Secrets**: Azure Key Vault for sensitive data
- **CORS**: Configured for your domains only

## 📊 Monitoring

View application insights:
```bash
az monitor app-insights query \
  --app <your-app-insights-name> \
  --analytics-query "traces | take 100"
```

## 🐛 Troubleshooting

### YouTube videos not working in Azure
YouTube blocks cloud provider IPs. Solutions:
1. Use the **Text Input** page to paste transcripts manually
2. Run the app locally for YouTube support
3. Focus on other content types (articles, text, PDF)

### PDF extraction fails
Ensure PDFs contain selectable text (not scanned images). Use OCR preprocessing if needed.

### Article scraping fails
Some sites block automated scraping. Try:
1. Different URLs from the same site
2. Copying content to Text Input manually
3. Converting to PDF first

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with [Azure Developer CLI](https://aka.ms/azd)
- Powered by [Azure OpenAI](https://azure.microsoft.com/products/ai-services/openai-service)
- UI inspiration from modern design systems

## 📞 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions  
- **Docs**: [Azure OpenAI Documentation](https://learn.microsoft.com/azure/ai-services/openai/)

---

**Demo live at**: [Your deployment URL]

Built with ❤️ using Azure + OpenAI
