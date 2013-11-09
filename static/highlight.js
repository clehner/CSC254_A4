window.onload = hash_change;
window.onhashchange = hash_change;

function hash_change(){
	if(location.hash.substr(1) && document.getElementById(location.hash.substr(1)))
		document.getElementById(location.hash.substr(1)).parentNode.className = 'highlight';
}
