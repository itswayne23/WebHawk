# WEBWATCH Cloud Edition

Checks all 13 configured URLs every 5 minutes. Confirms outages after 3 consecutive failed checks, sends Telegram outage/recovery messages, and sends an hourly report at 17 minutes past each UTC hour (22:47 India time). Incident state is persisted in `state/status.json`.

## Deploy
1. Create a **public** GitHub repository named WEBWATCH.
2. Upload all package contents to the repository root, including `.github/workflows/monitor.yml`.
3. In Settings → Secrets and variables → Actions, create repository secrets:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
4. In Settings → Actions → General → Workflow permissions, select **Read and write permissions**.
5. Ensure the workflow is on the default branch.
6. Open Actions → WEBWATCH monitoring → Run workflow.

## Free mobile push backup
Create an UptimeRobot account, add the same 13 URLs as HTTP(s) monitors, install its mobile app, allow notifications, and select the phone as a push contact for all monitors. UptimeRobot currently advertises 50 free monitors and 5-minute checks.

## Notes
Never commit bot tokens or `.env`. Public repo contents are visible to everyone. GitHub scheduled workflows run only from the default branch, can be delayed, and are disabled in public repositories after 60 days without repository activity. Standard GitHub-hosted Actions usage is currently free for public repositories. This checks public HTTP availability, not private application functionality.
