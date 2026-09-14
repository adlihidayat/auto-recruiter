import os

files = [
    "apps/frontend/src/app/(dashboard)/interviews/[interviewId]/candidates/[candidateId]/loading.tsx",
    "apps/frontend/src/app/(dashboard)/interviews/[interviewId]/loading.tsx",
    "apps/frontend/src/app/layout.tsx",
    "apps/frontend/src/features/candidates/components/CandidateReportView.tsx",
    "apps/frontend/src/features/interviews/components/InterviewDetailView.tsx"
]

for filepath in files:
    with open(filepath, "r") as f:
        content = f.read()
    new_content = content.replace("@/components/common/PageSkeletonWrapper", "@auto-recruiter/shared-ui")
    with open(filepath, "w") as f:
        f.write(new_content)
    print(f"Updated {filepath}")
