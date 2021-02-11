$(document).ready(function(){
     $('.sidenav').sidenav({ edge: "right", draggable: true });
     $('.parallax').parallax();
     $("#copyright").text(new Date().getFullYear());
  });