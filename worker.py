import os, sys, json, subprocess, requests, tempfile
from git import Repo
from dotenv import load_dotenv

load_dotenv()

data = json.loads(sys.argv[1])
brief = data["brief"]
task = data["task"]
email = data["email"]
nonce = data["nonce"]

# 1️⃣ Use LLM to generate minimal app
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompt = f"Generate a minimal webpage project that fulfills this brief: {brief}"
app_code = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}]
).choices[0].message.content

# 2️⃣ Create local temp dir
temp_dir = tempfile.mkdtemp()
repo_name = f"{task}-{nonce[:6]}"

# Write files
os.makedirs(f"{temp_dir}/{repo_name}", exist_ok=True)
with open(f"{temp_dir}/{repo_name}/index.html", "w") as f:
    f.write(app_code)

# LICENSE + README
with open(f"{temp_dir}/{repo_name}/LICENSE", "w") as f:
    f.write("MIT License")

with open(f"{temp_dir}/{repo_name}/README.md", "w") as f:
    f.write(f"# {repo_name}\n\n{brief}\n\n## License\nMIT")

# 3️⃣ Init Git + push
repo = Repo.init(f"{temp_dir}/{repo_name}")
origin_url = f"https://github.com/yourusername/{repo_name}.git"
repo.git.add(A=True)
repo.index.commit("Initial commit")
repo.create_remote('origin', origin_url)

repo.git.push("--set-upstream", "origin", "master")

# 4️⃣ Enable GitHub Pages
requests.post(
    f"https://api.github.com/repos/yourusername/{repo_name}/pages",
    headers={
        "Authorization": f"token {os.getenv('GITHUB_PAT')}",
        "Accept": "application/vnd.github.v3+json",
    },
    json={"source": {"branch": "master", "path": "/"}}
)

# 5️⃣ Prepare evaluation JSON
commit_sha = repo.head.commit.hexsha
pages_url = f"https://yourusername.github.io/{repo_name}/"
payload = {
    "email": email,
    "task": task,
    "round": 1,
    "nonce": nonce,
    "repo_url": origin_url,
    "commit_sha": commit_sha,
    "pages_url": pages_url
}

# 6️⃣ Retry POST to evaluation URL
evaluation_url = "https://evaluation.server/submit"
for delay in [1, 2, 4, 8, 16]:
    r = requests.post(evaluation_url, json=payload)
    if r.status_code == 200:
        print("✅ Submitted successfully")
        break
    else:
        print(f"Retrying in {delay}s...")
        time.sleep(delay)
