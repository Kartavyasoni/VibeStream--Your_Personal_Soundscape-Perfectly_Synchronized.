# Step 1: The "Identity" (Spotify Developer Setup)

Before we can pull data, we need to give your project permission to access Spotify’s library.

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2. Log in and click **"Create App."**
   - **App Name**: VibeStream-Intelligence
   - **Description**: Autonomous music intelligence platform for personalized discovery.
   - **Redirect URI**: `http://127.0.0.1:8080` (Important: We use this for local authentication).
3. Once created, go to **Settings** and copy your **Client ID** and **Client Secret.**