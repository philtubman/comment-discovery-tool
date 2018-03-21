(function () {

	var submitWords = function (newWord) {

			if (newWord) {
				chosenWords.push(newWord);
			}

			var f = document.forms['word-form'];

			chosenWords.forEach(function (word) {

				var input = document.createElement('input');
				input.type = 'text';
				input.name = 'chosen_words';
				input.value = word;
				f.appendChild(input);
			});

			f.submit();
		};

    var dataLoaded = function (queryResult) {

        var fill = d3.scale.category20();
        var width = 1000;
        var height = 500;

        /* This is where the result of the SQL qeury is given to the Javascript */
        //var queryResult = <?php echo json_encode($json); ?>;

        /* Here is the queryResult preprocessing, which will produce useful and reasonable values for the "size"  */
        /* Seems a little verbose atm, but will look at posibilities of condensing this further */
        var biggest_size;
        var smallest_size;

        for (var key in queryResult) {
            var current_value = Number(queryResult[key]["size"]);
            biggest_size = current_value;
            smallest_size = current_value;
            break;
        };

        for (var key in queryResult) {
            var current_value = Number(queryResult[key]["size"]);
            if (current_value > biggest_size) {biggest_size = current_value};
            if (current_value < smallest_size) {smallest_size = current_value};
        };

        var range = biggest_size - smallest_size;

        for (var key in queryResult) {
            var current_value = queryResult[key]["size"];
            var perentage = (current_value - smallest_size) / range;
            queryResult[key]["size"] = 100 * perentage + 14;
        }

        /* Now the data is ready to be processed by the d3 library*/
        d3.layout.cloud().size([width, height])
            .words(queryResult)
            .padding(5)
            // .rotate(function() { return ~~(Math.random() * 2) * 90; }) // Uncomment if you wish the words to be randomly rotated  
            .rotate(0)
            .font("sans-serif")
            .fontSize(function(d) { return d.size; })
            .on("end", draw)
            .start();

        function draw(words) {
            d3.select("#wordcloud").append("svg")
                .attr("width", width)
                .attr("height", height)
                .append("g")
                .attr("transform", "translate("+(width/2)+","+(height/2)+")")
                .selectAll("text")
                .data(words)
                .enter().append("text")
                .style("font-size", function(d) { return d.size + "px"; })
                .style("font-family", "sans-serif")
                .style("fill", function(d, i) { return fill(i); })
                .attr("text-anchor", "middle")
                .attr("transform", function(d) {
                    return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
                })
                // .text(function(d) { return d.text; });
                /* Below is a proof of concept of making each word clickable, while being able to reference what that word is */
                .text(function(d) { return d.text; })
                .on("click", function (d, i) {
					submitWords(d.text);
                });
        }
    }; // dataLoaded

    $.ajax({ url: '/data/terms', dataType: 'json' })
        .done(function(data, textStatus, jqXHR) {
            dataLoaded(data);
        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.log('Failed to load data. Error: ' + errorThrown);
        });

	$('.word-pill').on('closed.bs.alert', function () {

		chosenWords.splice(chosenWords.indexOf(this.dataset.word), 1);
		submitWords();
    });

    $(function () {

        $('.comment-link').click(function (e) {

            $.ajax({ url: '/data/logclick', method: 'POST'
                        , data: { commentId: e.target.dataset.commentId, csrfmiddlewaretoken: csrfToken }
            }).fail(function (jqXHR, textStatus, errorThrown) {
                    console.log('Failed to log click. Error: ' + errorThrown);
                });
        });
    });
})();
