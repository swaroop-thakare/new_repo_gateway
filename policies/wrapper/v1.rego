package arealis.compliance.wrapper.v1

import future.keywords.if

# Wrapper policy that handles direct input format
# This eliminates the 'input' key warning by creating proper input structure

# Pass through to routing policy with proper input structure
allow := data.arealis.compliance.routing.v1.allow
violations := data.arealis.compliance.routing.v1.violations
