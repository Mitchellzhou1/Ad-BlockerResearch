from bs4 import BeautifulSoup

# HTML code (replace this with your HTML)
html_code = """

<!DOCTYPE html>
<html>
<head>
		<title>CTFd</title>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<link rel="shortcut icon" href="/themes/core/static/img/favicon.ico" type="image/x-icon">
		<link rel="icon" href="/themes/core/static/img/favicon.ico" type="image/x-icon">
		<link rel="stylesheet" href="/themes/core/static/css/vendor/bootstrap.min.css">
		<link rel="stylesheet" href="/themes/core/static/css/vendor/fa-svg-with-js.css" />
		<link href='/themes/core/static/css/vendor/font.css' rel='stylesheet' type='text/css'>
		<link rel="stylesheet" href="/themes/core/static/css/jumbotron.css">
		<link rel="stylesheet" href="/themes/core/static/css/sticky-footer.css">
		<link rel="stylesheet" href="/themes/core/static/css/base.css">
		<link rel="stylesheet" type="text/css" href="/static/user.css">
		
	<link rel="stylesheet" href="/themes/core/static/css/challenge-board.css">

		
		<script src="/themes/core/static/js/vendor/moment.min.js"></script>
		<script src="/themes/core/static/js/vendor/nunjucks.min.js"></script>
		<script src="/themes/core/static/js/vendor/fontawesome-all.min.js"></script>
		<script type="text/javascript">
				var script_root = "";
		</script>
</head>
<body>
	<nav class="navbar navbar-expand-md navbar-dark bg-dark fixed-top">
		<div class="container">
			<a href="/" class="navbar-brand">CTFd</a>
			<button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#base-navbars"
					aria-controls="base-navbars" aria-expanded="false" aria-label="Toggle navigation">
				<span class="navbar-toggler-icon"></span>
			</button>
			<div class="collapse navbar-collapse" id="base-navbars">
				<ul class="navbar-nav mr-auto">
					

					
						<li class="nav-item">
							<a class="nav-link" href="/teams">Teams</a>
						</li>
					
					
						<li class="nav-item">
							<a class="nav-link" href="/scoreboard">Scoreboard</a>
						</li>
					
					<li class="nav-item">
						<a class="nav-link" href="/challenges">Challenges</a>
					</li>
				</ul>

				<hr class="d-sm-flex d-md-flex d-lg-none">

				<ul class="navbar-nav ml-md-auto d-block d-sm-flex d-md-flex">
					
						
						<li class="nav-item">
							<a class="nav-link" href="/team">Team</a>
						</li>
						<li class="nav-item">
							<a class="nav-link" href="/profile">Profile</a>
						</li>
						<li class="nav-item">
							<a class="nav-link" href="/logout">Logout</a>
						</li>
					
				</ul>
			</div>
		</div>
	</nav>

	<main role="main">
		

<div class="jumbotron">
	<div class="container">
		<h1>Challenges</h1>
	</div>
</div>






<div class="container">
	<div id='challenges-board'>
		<div class="text-center">
			<i class="fas fa-circle-notch fa-spin fa-3x fa-fw spinner"></i>
		</div>
	</div>
</div>

<input id="nonce" type="hidden" name="nonce" value="a98728f1a407469d4ae938bf45dec45e40f9c7664e35426104e44e00daa69db8cc054a208c03bdc70a20d31d98aa32d9c69d512c02d124036f3d37f84f4ad7ce">

<div class="modal fade" id="chal-window" tabindex="-1" role="dialog">
</div>


	</main>

	<footer class="footer">
		<div class="container text-center">
			<a href="https://ctfd.io">
				<small class="text-muted">Powered by CTFd</small>
			</a>
		</div>
	</footer>

	<script src="/themes/core/static/js/vendor/jquery.min.js"></script>
	<script src="/themes/core/static/js/vendor/marked.min.js"></script>
	<script src="/themes/core/static/js/vendor/bootstrap.bundle.min.js"></script>
	<script src="/themes/core/static/js/style.js"></script>
	<script src="/themes/core/static/js/ezq.js"></script>
	
	<script src="/themes/core/static/js/utils.js"></script>
	<script src="/themes/core/static/js/multi-modal.js"></script>
	
	<script src="/themes/core/static/js/chalboard.js"></script>
	
	<script src="/themes/core/static/js/style.js"></script>


	
</body>
</html>
"""
def code_breakdown(html_code):
	# Parse the HTML code with BeautifulSoup
	soup = BeautifulSoup(html_code, 'html.parser')

	# Find all <div> elements
	div_elements = soup.find_all('div')
	return div_elements


div_elements = code_breakdown(html_code)

for x, div in enumerate(div_elements):
    print(f"             {x}                 ")
    print(div.prettify())
