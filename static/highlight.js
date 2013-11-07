window.onload = function(){
	if(location.hash.substr(1) && document.getElementById(location.hash.substr(1)))
		document.getElementById(location.hash.substr(1)).parentNode.className = 'highlight';
};
