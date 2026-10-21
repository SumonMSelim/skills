# Accuracy protocol

A diagram is a claim about the system. Every element must trace to a line of IaC or code.

## Sources, in order of authority
1. Infrastructure as code: Terraform / CDK / CloudFormation / SAM in the repo. Resources,
   origins, behaviors, event source mappings, IAM policies, VPC endpoints.
2. Application code: handlers, SDK calls, env var wiring. This decides *what* crosses an
   arrow (GetItem vs Query, sync vs async, timeouts that change semantics).
3. CI/CD workflows: who deploys, via which role, what steps.
4. Design docs and READMEs last. They drift; when they disagree with code, follow code and
   tell the user.

## Before drawing, produce a component inventory
For each component: resource address, purpose, in-edges, out-edges (with the API action).
Delete anything you cannot cite. Scaffolding that exists in IaC but is unused by code is
drawn but marked as such only if the user wants it; otherwise leave it out and say so.

## Arrow rules
- Direction = who initiates the call. Event source mappings point from the source to the
  consumer. Pub/sub points from publisher to topic to subscriber.
- Label with the concrete action from the IAM policy or SDK call.
- Cache behaviors: name the path pattern and cache policy as configured.
- Do not draw "implied" connections (e.g. every Lambda → CloudWatch). Put shared
  services in the platform strip instead.

## Common mistakes (seen in real drafts, do not repeat)
- Copying a "typical" value (CIDR, TTL, region) instead of reading the variable's default.
- Calling a call "non-blocking" or "fire-and-forget" when the code awaits it.
- Claiming a CLI or service assumes a role when it only uses ambient credentials.
- Taking the auth mechanism from a design doc that the code has since changed.
- Putting instance sizes, node counts or provisioned capacity in sub-labels.
- Drawing every resource in the account. Draw the workload the reader asked about.

## Final review
Re-read the IaC once more after the render and tick each component and each arrow.
Report any simplification explicitly (e.g. an omitted second edge to avoid a crossing).
