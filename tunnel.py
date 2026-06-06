from pyngrok import ngrok

ngrok.set_auth_token("3EmRLeylh3gTfg6LGZ0eCmYQEfU_3ADBuK7X2rnmVxdgLk6bD")
tunnel = ngrok.connect(5001, bind_tls=True)
print(f"\n{'='*60}")
print(f"  Tunel activo! Comparti esta URL:")
print(f"  {tunnel.public_url}")
print(f"{'='*60}\n")
print("  Presiona Ctrl+C para cerrar.\n")

try:
    ngrok_process = ngrok.get_ngrok_process()
    ngrok_process.proc.wait()
except KeyboardInterrupt:
    print("\nCerrando tunel...")
    ngrok.kill()
