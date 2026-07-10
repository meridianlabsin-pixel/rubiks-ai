try:
    import speedtest
    _SPEEDTEST_AVAILABLE = True
except ImportError:
    _SPEEDTEST_AVAILABLE = False

def run_speed_test() -> str:
    """
    Runs a network diagnostic using Speedtest.net servers to measure Download/Upload bandwidth and Latency (Ping).
    This process takes about 15-20 seconds to complete.
    """
    if not _SPEEDTEST_AVAILABLE:
        return "Speed test unavailable: 'speedtest-cli' package is not installed. Run: pip install speedtest-cli"

    try:
        st = speedtest.Speedtest()
        
        # Get best server based on ping
        st.get_best_server()
        
        # Measure download and convert to Mbps
        download_speed = st.download() / 1_000_000
        
        # Measure upload and convert to Mbps
        upload_speed = st.upload() / 1_000_000
        
        # Get ping
        ping = st.results.ping
        
        # Get server info
        server = st.results.server['sponsor']
        location = st.results.server['name']
        
        return (f"Network Diagnostics Complete:\n"
                f"Download: {download_speed:.2f} Mbps\n"
                f"Upload: {upload_speed:.2f} Mbps\n"
                f"Ping: {ping:.0f} ms\n"
                f"Server: {server} ({location})")
    except Exception as e:
        return f"Failed to run network speed test: {str(e)}"
