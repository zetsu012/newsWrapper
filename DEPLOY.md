# Deploying AI News Aggregator to Vercel

## Prerequisites

1. **GitHub Repository**: Your code is already on GitHub at `https://github.com/zetsu012/newsWrapper.git`
2. **Vercel Account**: Sign up at [vercel.com](https://vercel.com) if you haven't already
3. **API Credentials**: You'll need Reddit and NewsAPI credentials for production

## Step-by-Step Deployment

### 1. Connect GitHub to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your GitHub repository: `zetsu012/newsWrapper`
4. Vercel will automatically detect it as a Python project

### 2. Configure Environment Variables

In Vercel dashboard, go to your project settings and add these environment variables:

**Required for Production:**
```
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=AI News Aggregator v1.0
NEWSAPI_KEY=your_newsapi_key
```

**Optional (with defaults):**
```
CACHE_TTL=300
ENABLE_CACHE=false
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=3600
TOTAL_ARTICLES=20
```

### 3. Configure Build Settings

Vercel should automatically detect the settings from `vercel.json`, but verify:

- **Framework Preset**: Other
- **Build Command**: (leave empty)
- **Output Directory**: (leave empty)
- **Install Command**: `pip install -r requirements-vercel.txt`

### 4. Deploy

1. Click "Deploy"
2. Vercel will build and deploy your application
3. You'll get a live URL like `https://news-wrapper-xyz.vercel.app`

## API Endpoints

Once deployed, your API will be available at:

- **Main endpoint**: `https://your-domain.vercel.app/ai-news`
- **Health check**: `https://your-domain.vercel.app/health`
- **API docs**: `https://your-domain.vercel.app/docs`
- **Sources info**: `https://your-domain.vercel.app/sources`

## Testing the Deployment

### Test Mode (No API Keys Needed)
If you don't set real API credentials, the app will automatically use mock data:
```bash
curl https://your-domain.vercel.app/ai-news
```

### Production Mode (With Real API Keys)
Set the environment variables in Vercel dashboard and the app will fetch real data.

## Getting API Credentials

### Reddit API
1. Go to https://www.reddit.com/prefs/apps
2. Create a new application (select "script")
3. Copy the client ID and secret

### NewsAPI
1. Sign up at https://newsapi.org/
2. Get your free API key from the dashboard

## Environment Variables in Vercel

1. Go to your Vercel project dashboard
2. Click "Settings" → "Environment Variables"
3. Add each variable with its value
4. Redeploy the project

## Vercel Limitations to Consider

- **Function Timeout**: 30 seconds max (configured in vercel.json)
- **Memory**: 1024MB max for Hobby plan
- **Cold Starts**: First request might be slower
- **Redis**: Not available on Vercel (caching is disabled by default)

## Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure all dependencies are in `requirements-vercel.txt`
2. **Timeout**: API requests to external services might timeout - the app handles this gracefully
3. **Environment Variables**: Double-check they're set correctly in Vercel dashboard

### Debug Steps:

1. Check Vercel function logs in the dashboard
2. Test the `/health` endpoint first
3. Use the `/docs` endpoint to explore the API

## Performance Optimization for Vercel

The app is configured for Vercel with:

- ✅ Async/await throughout for better performance
- ✅ Graceful error handling for API timeouts
- ✅ Mock data fallback for testing
- ✅ Optimized dependencies list
- ✅ 30-second timeout configuration

## Custom Domain (Optional)

1. In Vercel dashboard, go to "Settings" → "Domains"
2. Add your custom domain
3. Follow Vercel's DNS configuration instructions

Your AI News Aggregator API will be live and ready to serve trending AI news! 🚀
