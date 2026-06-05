# Uptime Robot Setup Guide

## Purpose
This guide will help you set up Uptime Robot to keep your Render backend active 24/7, ensuring your MediScan app works reliably on your phone at all times.

## Prerequisites
- Your backend is deployed on Render: `https://mediscan-ai-2-by4n.onrender.com`
- You have an Uptime Robot account (free tier works great!)

## Step-by-Step Setup

### 1. Sign Up / Log In to Uptime Robot
- Go to: https://uptimerobot.com/
- Create a free account or log in to your existing account

### 2. Add a New Monitor
1. Click **+ Add New Monitor** button
2. Select **HTTP(s)** as the monitor type
3. Configure the monitor:
   - **Friendly Name**: `MediScan Backend (Render)`
   - **URL (or IP)**: `https://mediscan-ai-2-by4n.onrender.com/health`
   - **Monitoring Interval**: Choose 5 minutes (the shortest free tier interval)
4. Click **Create Monitor**

### 3. Verify the Monitor
- Uptime Robot will start pinging your backend every 5 minutes
- This prevents Render from putting your backend to sleep due to inactivity
- You'll receive email alerts if the monitor detects downtime

## Why This Works
- Render free tier automatically spins down inactive services after ~15 minutes
- Uptime Robot pings your `/health` endpoint every 5 minutes to keep it active
- Your backend stays responsive so your phone can always connect to it

## Health Endpoint
Your backend already has a built-in health endpoint:
- **URL**: `https://mediscan-ai-2-by4n.onrender.com/health`
- **Response**: `{"ok": true}`
- This is perfect for Uptime Robot monitoring

## Additional Tips
1. **Set Up Alerts**: Configure Uptime Robot to send you email/SMS alerts if your backend goes down
2. **Check Dashboard**: Use Uptime Robot's dashboard to monitor your backend's uptime statistics
3. **Test the App**: After setup, test your app on your phone at: `https://mediscan-ai-rh98.vercel.app`

## Monitor Configuration Summary
- **Type**: HTTP(s)
- **URL**: `https://mediscan-ai-2-by4n.onrender.com/health`
- **Interval**: 5 minutes
- **Timeout**: 30 seconds (default)
- **Alerts**: Email (free)
