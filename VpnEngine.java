package org.test.bughunter;

import android.net.VpnService;
import android.os.ParcelFileDescriptor;
import android.content.Intent;
import android.util.Log;

public class VpnEngine extends VpnService {
    private ParcelFileDescriptor vpnInterface = null;

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null && "STOP".equals(intent.getAction())) {
            stopVpn();
            return START_NOT_STICKY;
        }

        Builder builder = new Builder();
        try {
            builder.setSession("BugHunter")
                   .setMtu(1500)
                   .addAddress("10.0.0.1", 24)
                   .addRoute("0.0.0.0", 0)
                   .addDnsServer("8.8.8.8");
            vpnInterface = builder.establish();
            Log.d("BugHunter", "VPN Service Started Successfully");
        } catch (Exception e) {
            Log.e("BugHunter", "Failed to establish VPN", e);
        }
        return START_STICKY;
    }

    private void stopVpn() {
        try {
            if (vpnInterface != null) {
                vpnInterface.close();
                vpnInterface = null;
            }
        } catch (Exception e) {}
        stopSelf();
    }
}
