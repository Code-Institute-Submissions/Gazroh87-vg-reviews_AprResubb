$(document).ready(function(){
     $('.sidenav').sidenav({ edge: "right", draggable: true });
     $('.parallax').parallax();
     $(':header').css("font-family","'Press Start 2P'", "cursive")
     $("#copyright").text(new Date().getFullYear());
  });