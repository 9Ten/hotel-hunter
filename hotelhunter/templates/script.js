<script type="text/javascript">
  $(document).ready(function(){
    // Add smooth scrolling to all links in navbar + footer link
    $(".navbar a, footer a[href='#myPage']").on('click', function(event) {
      // Make sure this.hash has a value before overriding default behavior
      if (this.hash !== "") {
        // Prevent default anchor click behavior
        event.preventDefault();

        // Store hash
        var hash = this.hash;

        // Using jQuery's animate() method to add smooth page scroll
        // The optional number (900) specifies the number of milliseconds it takes to scroll to the specified area
        $('html, body').animate({
          scrollTop: $(hash).offset().top
        }, 900, function(){

          // Add hash (#) to URL when done scrolling (default click behavior)
          window.location.hash = hash;
        });
      } // End if
    });

    $(window).scroll(function() {
      $(".slideanim").each(function(){
        var pos = $(this).offset().top;

        var winTop = $(window).scrollTop();
          if (pos < winTop + 600) {
            $(this).addClass("slide");
          }
      });
    });
  })
</script>


<script type="text/javascript">

        jQuery(document).ready(function () {
            $("#input-21f").rating({
                starCaptions: function (val) {
                    if (val < 3) {
                        return val;
                    } else {
                        return 'high';
                    }
                },
                starCaptionClasses: function (val) {
                    if (val < 3) {
                        return 'label label-danger';
                    } else {
                        return 'label label-success';
                    }
                },
                hoverOnClear: false
            });
            var $inp = $('#rating-input');

            $inp.rating({
                min: 0,
                max: 5,
                step: 1,
                size: 'lg',
                showClear: false
            });

            $('#btn-rating-input').on('click', function () {
                $inp.rating('refresh', {
                    showClear: true,
                    disabled: !$inp.attr('disabled')
                });
            });


            $('.btn-danger').on('click', function () {
                $("#kartik").rating('destroy');
            });

            $('.btn-success').on('click', function () {
                $("#kartik").rating('create');
            });

            $inp.on('rating.change', function () {
                alert($('#rating-input').val());
            });


            $('.rb-rating').rating({
                'showCaption': true,
                'stars': '3',
                'min': '0',
                'max': '3',
                'step': '1',
                'size': 'xs',
                'starCaptions': {0: 'status:nix', 1: 'status:wackelt', 2: 'status:geht', 3: 'status:laeuft'}
            });
            $("#input-21c").rating({
                min: 0, max: 10, step: 0.5, size: "xs", stars: "10"
            });


            /// string format ///
            Number.prototype.format = function(n, x) {
                var re = '\\d(?=(\\d{' + (x || 3) + '})+' + (n > 0 ? '\\.' : '$') + ')';
                return this.toFixed(Math.max(0, ~~n)).replace(new RegExp(re, 'g'), '$&,');
              };

              search_result({{ hotels_all|safe }})
              recommend_result({{ hotels_rec|safe }})



              /// icon feature ///
              function get_icon(adventages) {
                icon = ""
                switch (adventages) {
                  case 0:
                    icon = '<p class="glyphicon glyphicon-usd" style="color: black; font-size: 14px;"><b> Price</b></p><br>'
                    break;
                  case 2:
                    icon = '<p class="glyphicon glyphicon-cutlery" style="color: black; font-size: 14px;"><b> Restaurants</b></p><br>'
                    break;
                  case 5: // Convenient Store CONVSTORE
                    icon = '<p class="glyphicon glyphicon glyphicon-apple" style="color: black; font-size: 14px;"><b> Convenient Store</b></p><br>'
                    break;
                  case 1:
                    icon = '<p class="glyphicon glyphicon-plane" style="color: black; font-size: 14px;"><b> Near Station</b></p><br>'
                    break;
                  case 3:
                    icon = '<p class="glyphicon glyphicon-film" style="color: black; font-size: 14px;"><b> Entertainments</b></p><br>'
                    break;
                  case 4:
                    icon = '<p class="glyphicon glyphicon-shopping-cart" style="color: black; font-size: 14px;"><b> Shopping Mall</b></p><br>'
                    break;
                  default:
                    icon = '<p class="glyphicon glyphicon-remove" style="color: black; font-size: 14px;"><b> No data </b></p><br>'
                    break;

                }
                return icon
              }

              function get_star(stars) {
                html3 = ''
                if (stars == 0) {
                  return '<br>'
                }
                for (var i = 0; i < stars; i++) {
                  html3+='<label class="glyphicon glyphicon-star" style="color: #ffd11a;"></label>'
                }
                return html3
              }

              /// change result ///
              function search_result(data) {
                html =''
                $('#result').css("height","1600px")
                if (data.length != 0) {
                for (var i = 0; i < data.length; i++) {
                  if(data[i].price != null || data[i].rating != null){
                    html+='<div class="list"><div class="col-sm-6"><a target="_blank" href="#"><img class="pic" src="data:image/jpeg;base64,'+data[i].image+'" alt="'+data[i].name+'"></a></div><div class="col-sm-6"><div class="detail"><a href="#" style="text-decoration: none;"><p class="desc1">'+data[i].name+'</p><div class="desc2">'+get_star(data[i].stars)+'</div><p class="desc3">'+data[i].rating+'</p><p class="desc4">THB <a href="#">'+(data[i].price.format())+'</a></p></a><div class="booklist"><center><button data-toggle="modal" data-target="#book" class="btn btn-warning btn-md getloader" type="button"  >>> Book Now</button></center></div></div></div></div><br>'
                    }
                  }
                  $('#result').html(html)
                }else {
                    $('#result').html('<center><h3>Sorry, No results found</h3></center>')
                }
              }
              /// change recommend ///
              function recommend_result(data) {
                html =''
                html1 =''
                for (var i = 0; i < data.length; i++) {
                  if (i==0) {
                    html += '<div class="item active"><center>'
                  }else{
                    html+= '<div class="item"><center>'
                  }
                  for (var j = 0; j < 3; j++) {
                    if(i>data.length){break;}
                    // image = 'img/'+findAndReplace(data[i].name,' ','%20')+'.jpg'
                    html+='<div class="col-sm-4"><div class="fff"><a href="#"><img src="data:image/jpeg;base64,'+data[i].image+'" alt="'+data[i].name+'" height="200em" width="100%" style="border-radius: 4px 4px 0px 0px;"></a><a href="#"><h6>'+data[i].name+' </h6></a>'+get_star(data[i].stars)+'<hr><label class="recRate"><b>Rating :</b> '+data[i].rating+'</label><label class="recPrice"><b>Price :</b> THB '+data[i].price.format()+'</label><br><div style="text-align: left; margin-left: 10px;">'+get_icon(data[i].adventages[0])+get_icon(data[i].adventages[1])+get_icon(data[i].adventages[2])+'</div><center><a class="btn btn-mini btn-success getloader" type="button"  data-toggle="modal" data-target="#book" href="#">» Book Now</a></center></div></div>'
                    i++;
                  }
                  i--;
                  html+='</center></div>'
              }

              for (var i = 0; i < data.length; i++) {
                if (i==0) {
                  html1 += '<div class="item active"><center>'
                }else{
                  html1+= '<div class="item"><center>'
                }
                // image = 'img/'+findAndReplace(data[i].name,' ','%20')+'.jpg'
                html1+='<div class="fff"><a href="#"><img src="data:image/jpeg;base64,'+data[i].image+'" alt="" height="200em" width="100%" style="border-radius: 4px 4px 0px 0px;"></a><a href="#"><h6>'+data[i].name+' </h6></a>'+get_star(data[i].stars)+'<hr><label class="recRate"><b>Rating :</b> '+data[i].rating+'</label><label class="recPrice"><b>Price :</b> THB '+data[i].price.format()+'</label><br><div style="text-align: left; margin-left: 10px;">'+get_icon(data[i].adventages[0])+get_icon(data[i].adventages[1])+get_icon(data[i].adventages[2])+'</div><center><a class="btn btn-mini btn-success getloader" type="button"  data-toggle="modal" data-target="#book" href="#">» Book Now</a></center></div></div></center></div>'

            }
            $('#myCarousel .carousel-inner').html(html)
            $('#carouselInMobile .carousel-inner').html(html1)
          }
        });
</script>
