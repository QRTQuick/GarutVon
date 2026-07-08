Quick Vercel deployment notes for GarutVON

1) Create a Vercel project and point it to this repository.
   - Framework Preset: Other
   - Root Directory: ./
   - Leave Build & Install commands blank (Vercel will use the Python builder defined in vercel.json)

2) Set these Environment Variables in Vercel (Production + Preview):
   - DATABASE_URL = <your Neon DB URL>
   - SECRET_KEY = <your Flask secret key>
   - MAILJET_API_KEY = <mailjet key>
   - MAILJET_SECRET_KEY = <mailjet secret>
   - PUBLIC_BASE_URL = https://your-domain.example
   - DOWNLOAD_URL = https://your-download-host.example
   - LATEST_VERSION = 1.0.0
   - DONATION_URL = https://your-donation.example

3) Stop tracking local `.env` (if committed):

```powershell
git rm --cached .env
git add .gitignore
git commit -m "Stop tracking env and add Vercel config"
git push
```

4) After deploy, update `robots.txt` and `sitemap.xml` by replacing `PUBLIC_BASE_URL` with your real domain.

5) Verify endpoints:
   - /api/health
   - /api/version
   - /api/supported-image-formats
   - /api-testing (webapp testing page)

6) Optional hardening before public launch:
   - Clean `requirements-prod.txt` to remove duplicates.
   - Configure rate limiting and monitoring.
   - Add HTTPS-only cookie and secure session settings in production.

