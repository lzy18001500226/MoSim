#!/usr/bin/env node
/**
 * Create a GA4 property and web data stream via Google Analytics Admin API
 *
 * Setup:
 * 1. npm install @google-analytics/admin
 * 2. Enable Analytics Admin API: https://console.cloud.google.com/apis/library/analyticsadmin.googleapis.com
 * 3. Authenticate: gcloud auth application-default login
 * 4. Run: node scripts/setup-ga4.mjs
 */

import { AnalyticsAdminServiceClient } from '@google-analytics/admin';

async function createGA4Property() {
  const client = new AnalyticsAdminServiceClient();

  try {
    console.log('🔍 Fetching your Google Analytics accounts...\n');

    // List accounts
    const [accounts] = await client.listAccounts();

    if (accounts.length === 0) {
      console.error('❌ No Google Analytics accounts found.');
      console.error('   Create one at: https://analytics.google.com/');
      process.exit(1);
    }

    console.log('📊 Available accounts:');
    accounts.forEach((account, i) => {
      console.log(`   ${i + 1}. ${account.displayName} (${account.name})`);
    });

    // Use first account (or you can add prompt here)
    const selectedAccount = accounts[0];
    console.log(`\n✓ Using account: ${selectedAccount.displayName}\n`);

    // Create GA4 property
    console.log('🏗️  Creating GA4 property for Agor...');
    const [property] = await client.createProperty({
      property: {
        parent: selectedAccount.name,
        displayName: 'Agor Live',
        propertyType: 'PROPERTY_TYPE_ORDINARY',
        timeZone: 'America/Los_Angeles',
        currencyCode: 'USD',
        industryCategory: 'TECHNOLOGY',
      },
    });

    console.log(`✓ Property created: ${property.displayName}`);
    console.log(`  Property ID: ${property.name}\n`);

    // Create web data stream
    console.log('🌐 Creating web data stream...');
    const [dataStream] = await client.createDataStream({
      parent: property.name,
      dataStream: {
        type: 'WEB_DATA_STREAM',
        displayName: 'Agor Website',
        webStreamData: {
          defaultUri: 'https://agor.live',
        },
      },
    });

    console.log(`✓ Data stream created: ${dataStream.displayName}\n`);

    // Extract measurement ID
    const measurementId = dataStream.webStreamData?.measurementId;

    console.log('━'.repeat(60));
    console.log('🎉 SUCCESS! Your GA4 property is ready!\n');
    console.log(`📊 Property: ${property.displayName}`);
    console.log(`🆔 Measurement ID: ${measurementId}\n`);
    console.log('Next steps:');
    console.log(`  1. Add to your .env.local:`);
    console.log(`     NEXT_PUBLIC_GA_ID=${measurementId}`);
    console.log(`  2. Rebuild your site: pnpm build`);
    console.log('━'.repeat(60));
  } catch (error) {
    console.error('❌ Error:', error.message);

    if (error.message.includes('Could not load the default credentials')) {
      console.error('\n💡 Solution: Run this first:');
      console.error('   gcloud auth application-default login');
    } else if (error.message.includes('API has not been used')) {
      console.error('\n💡 Solution: Enable the Analytics Admin API:');
      console.error(
        '   https://console.cloud.google.com/apis/library/analyticsadmin.googleapis.com'
      );
    }

    process.exit(1);
  }
}

createGA4Property();
