<html>
    <head>
      <title>{{title}}</title>
      <style>
        body {
          background-color:#FFE9D3;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
          margin:0px;
        }
        header {
          background-color:#677B8D;
          width:100%;
          height:50px;
          color:white;
        }
        .main {
          width:800px;
          margin:0 auto;
        }
        .chat {
          width:800px;
          height:40px;
          border: 1px solid transparent;
        }
        form {
          margin-top:20px;
          margin-bottom:20px;
        }
        .submit {
          background-color: #70D5FC;
          width:100px;
          padding:10px;
          float:right;
          border-radius:5px;
          border:1px solid transparent;
        }
        article {
          margin-top:50px;
        }
        .reply {
          font-weight:100px;
          height:70px;
          width:100%;
        }
        .reply img {
          margin-right:10px;
        }
        .img-handler {
          text-align:center;
          width:60px;
          margin-right:20px;
          display: inline-block;
        }
        .txt-handler {
          text-align: left;
          display:inline-block;
          position:relative;
          top:-30px;
        }
      </style>
    </head>
    <body>
      <header>
        <div class="main">
          <h1>{{title}}</h1>
        </div>
      </header>
      <img src="" />
      <div class="main">
        <form>
          <input class="chat" type="text" name="chat" />
        </form>
        <button class="submit">Chat!</button>
      </div>
      <article>
        <div class="main">
          <div class="chats">
          </div>
      </div>
      </article>

      <!-- JAVASCRIPT -->
      <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.0.0/jquery.min.js"></script>
      <script type="text/javascript">
      $(".submit").click(function() {
        var chat = $(".chat" ).val();

        $(".chats").append("<div class='reply'>"
                            + "<div class='img-handler'><img src='https://garethjones-apps.s3.amazonaws.com/apps/valleybot/personLogo.png' /></div>"
                            + "<div class='txt-handler'>" + chat + "</div>"
                            + "</div>");


        $.get( "/bot?chat=" + chat).done(function( data ) {
          $(".chats").append("<div class='reply'>"
                              + "<div class='img-handler'><img src='https://garethjones-apps.s3.amazonaws.com/apps/valleybot/botLogo.png' /></div>"
                              + "<div class='txt-handler'>" + data['data'] + "</div>"
                              + "</div>");
        });
      });
      </script>
    </body>
</html>
