from sys import argv, stderr
import requests

if __name__ == "__main__":
  if len(argv) < 2:
    print("usage: uploadfile.py <audio_name.mp3>", file=stderr)
    raise SystemExit
  
  f = open(f"../audio/{argv[1]}", "rb")
  r = requests.post("http://localhost:25623", files={"file": f})
  print(r)
  print(r.text)
