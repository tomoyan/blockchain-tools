$(document).ready(function(){
    $.ajax(document.follower_api,
    {
        dataType: 'json', // type of response data
        timeout: 60000,     // timeout milliseconds
        success: function (data, status, xhr) {   // success callback function
            var size = Object.keys(data).length;
            $("#followerSize").html(size);
            // console.log(Object.keys(data).length);

            // liStr holds html list
            var liStr = ``;
            if (jQuery.isEmptyObject(data)) {
                liStr = `
                <li class="list-group-item" data-field=><span>No Follower Data</span></li>`;
                $("#followerResult").append(liStr);
            }
            else {
               $.each(data, function(key, data){
                    if (data) {
                    liStr = `
                        <li class="list-group-item" data-field=>
                            <span><img src="https://images.blurt.blog/u/${key}/avatar/small"
                                    onerror="this.onerror=null;
                                    this.src='{{ url_for('static', filename='images/blurt_logo.png') }}'"
                                    alt="profile_image"
                                    class="img-thumbnail rounded-circle float-left mr-3"
                                    width="auto"></span>
                            <span><a class="text-blurt font-weight-bold mr-3" href="https://blurt.blog/@${key}">${key}</a></span>
                            <span class="badge badge-blurt font-weight-light">Following</span>
                        </li>`;
                    }
                    else {
                    liStr = `
                        <li class="list-group-item" data-field=>
                            <span><img src="https://images.blurt.blog/u/${key}/avatar/small"
                                    onerror="this.onerror=null;
                                    this.src='{{ url_for('static', filename='images/blurt_logo.png') }}'"
                                    alt="profile_image"
                                    class="img-thumbnail rounded-circle float-left mr-3"
                                    width="auto"></span>
                            <span><a class="text-blurt font-weight-bold" href="https://blurt.blog/@${key}">${key}</a></span>
                        </li>`;
                    }

                    $("#followerResult").append(liStr);
                });
           }
        },
        error: function (jqXhr, textStatus, errorMessage) { // error callback
            $("#followerResult").append('Error: ' + errorMessage);
        }
    });

    $.ajax(document.following_api,
    {
        dataType: 'json', // type of response data
        timeout: 60000,     // timeout milliseconds
        success: function (data, status, xhr) {   // success callback function
            var size = Object.keys(data).length;
            $("#followingSize").html(size);
            // console.log(Object.keys(data).length);

            // liStr holds html list
            var liStr = ``;
            if (jQuery.isEmptyObject(data)) {
                liStr = `
                <li class="list-group-item" data-field=><span>No Following Data</span></li>`;
                $("#followingResult").append(liStr);
            }
            else {
               $.each(data, function(key, data){
                    if (data) {
                    liStr = `
                        <li class="list-group-item" data-field=>
                            <span><img src="https://images.blurt.blog/u/${key}/avatar/small"
                                    onerror="this.onerror=null;
                                    this.src='{{ url_for('static', filename='images/blurt_logo.png') }}'"
                                    alt="profile_image"
                                    class="img-thumbnail rounded-circle float-left mr-3"
                                    width="auto"></span>
                            <span><a class="text-blurt font-weight-bold mr-3" href="https://blurt.blog/@${key}">${key}</a></span>
                            <span class="badge badge-blurt font-weight-light">Follows you</span>
                        </li>`;
                    }
                    else {
                    liStr = `
                        <li class="list-group-item" data-field=>
                            <span><img src="https://images.blurt.blog/u/${key}/avatar/small"
                                    onerror="this.onerror=null;
                                    this.src='{{ url_for('static', filename='images/blurt_logo.png') }}'"
                                    alt="profile_image"
                                    class="img-thumbnail rounded-circle float-left mr-3"
                                    width="auto"></span>
                            <span><a class="text-blurt font-weight-bold" href="https://blurt.blog/@${key}">${key}</a></span>
                        </li>`;
                    }

                    $("#followingResult").append(liStr);
                });
           }
        },
        error: function (jqXhr, textStatus, errorMessage) { // error callback
            $("#followingResult").append('Error: ' + errorMessage);
        }
    });

    $.ajax(document.mute_api,
    {
        dataType: 'json', // type of response data
        timeout: 60000,     // timeout milliseconds
        success: function (data, status, xhr) {   // success callback function
            var size = Object.keys(data['muting']).length + Object.keys(data['muter']).length;
            $("#muteSize").html(size);
            // console.log(data['muter']);
            // console.log(data['muting']);
            // console.log(Object.keys(data).length);

            // liStr holds html list
            var liStr = ``;
            if (jQuery.isEmptyObject(data['muting'])) {
                liStr = `
                <li class="list-group-item" data-field=><span>Not Muting Anybody</span></li>`;
                $("#mutingResult").append(liStr);
            }
            else {
               $.each(data['muting'], function(index, value){
                    liStr = `
                        <li class="list-group-item" data-field=>
                            <span><img src="https://images.blurt.blog/u/${value}/avatar/small"
                                    onerror="this.onerror=null;
                                    this.src='{{ url_for('static', filename='images/blurt_logo.png') }}'"
                                    alt="profile_image"
                                    class="img-thumbnail rounded-circle float-left mr-3"
                                    width="auto"></span>
                            <span><a class="text-blurt font-weight-bold mr-3" href="https://blurt.blog/@${value}">${value}</a></span>
                        </li>`;

                    $("#mutingResult").append(liStr);
                });
           }

            if (jQuery.isEmptyObject(data['muter'])) {
                liStr = `
                <li class="list-group-item" data-field=><span>Not Muted by Anybody</span></li>`;
                $("#muteResult").append(liStr);
            }
            else {
               $.each(data['muter'], function(index, value){
                    liStr = `
                        <li class="list-group-item" data-field=>
                            <span><img src="https://images.blurt.blog/u/${value}/avatar/small"
                                    onerror="this.onerror=null;
                                    this.src='{{ url_for('static', filename='images/blurt_logo.png') }}'"
                                    alt="profile_image"
                                    class="img-thumbnail rounded-circle float-left mr-3"
                                    width="auto"></span>
                            <span><a class="text-blurt font-weight-bold mr-3" href="https://blurt.blog/@${value}">${value}</a></span>
                        </li>`;

                    $("#muteResult").append(liStr);
                });
           }

        },
        error: function (jqXhr, textStatus, errorMessage) { // error callback
            $("#muteResult").append('Error: ' + errorMessage);
        }
    });
});
