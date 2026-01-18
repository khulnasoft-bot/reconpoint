//go:build tools
package tools

import (
	_ "github.com/jaeles-project/gospider/cmd/gospider"
	_ "github.com/tomnomnom/gf/cmd/gf"
	_ "github.com/tomnomnom/unfurl/cmd/unfurl"
	_ "github.com/tomnomnom/waybackurls/cmd/waybackurls"
	_ "github.com/projectdiscovery/httpx/cmd/httpx"
	_ "github.com/projectdiscovery/subfinder/v2/cmd/subfinder"
	_ "github.com/projectdiscovery/chaos-client/cmd/chaos"
	_ "github.com/projectdiscovery/nuclei/v3/cmd/nuclei"
	_ "github.com/projectdiscovery/naabu/v2/cmd/naabu"
	_ "github.com/hakluke/hakrawler/cmd/hakrawler"
	_ "github.com/lc/gau/v2/cmd/gau"
	_ "github.com/owasp-amass/amass/v3/cmd/amass"
	_ "github.com/ffuf/ffuf/cmd/ffuf"
	_ "github.com/projectdiscovery/tlsx/cmd/tlsx"
	_ "github.com/hahwul/dalfox/v2/cmd/dalfox"
	_ "github.com/projectdiscovery/katana/cmd/katana"
	_ "github.com/dwisiswant0/crlfuzz/cmd/crlfuzz"
	_ "github.com/sa7mon/s3scanner/cmd/s3scanner"
)
