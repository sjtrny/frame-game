import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html

dash.register_page(__name__, path="/about", title="About | Frame Game Solver")

layout = dbc.Container(
    [
        dbc.Row(
            html.A(
                html.H1("Frame Game Solver"),
                href="/",
                className="text-decoration-none text-reset",
            )
        ),
        dbc.Row(
            dbc.Col(
                [
                    dcc.Markdown(
                        """
                        ## Shazam

                        Solving Siracusa's Frame Game is the visual equivalent
                        of Shazam.

                        Shazam is a music recognition service
                        that is able to identify songs based on arbitrary, noisy and short samples
                        of the original source. Most people know Shazam as an app
                        for mobile devices. However Shazam existed before
                        the smartphone as a telephone based service.

                        The suprising thing about Shazam is that it doesn't use
                        Machine Learning to recognise songs. Instead Shazam relies
                        on matching carefully crafted features between songs and a clever scoring strategy.

                        We can do the same for the Frame Game.

                        ## Frame Game

                        #### Keypoints

                        To match a test image against sources we need a way to
                        describe the visual structure of an image. This can be
                        achieved by using a feature detection technique like [SIFT](https://www.vlfeat.org/api/sift.html), SURF or others.

                        An example of the keypoints generated for the hint from frame 18 is shown below.

                    """
                    ),
                    html.Img(
                        src="/assets/frame18-1-kps.png",
                        style={"width": "240px"},
                        className="mb-3",
                    ),
                    dcc.Markdown(
                        """
                        The keypoints are indicated by the circles, with:
                        - the centre denoting the keypoint coordinates
                        - the diameter denoting the scale of the feature
                        - the radial line denoting the direction of the feature.

                        This image is from Willy Wonka & the Chocolate Factory (1971) and the
                        entire original frame with all keypoints is shown below.

                    """
                    ),
                    html.Img(
                        src="/assets/frame18-full-kps.jpg",
                        style={"width": "100%"},
                        className="mb-3",
                    ),
                    dcc.Markdown(
                        """
                        Placing the hint image and the cropped area of the source image
                        side by side (below, left and right respectively) reveals many coinciding keypoints.
                    """
                    ),
                    html.Img(
                        src="/assets/frame18-1-kps.png",
                        style={"width": "240px"},
                        className="mb-3",
                    ),
                    html.Img(
                        src="/assets/frame18-full-kps-zoom.jpg",
                        style={"width": "240px"},
                        className="mb-3",
                    ),
                    dcc.Markdown(
                        """
                        #### Matching Strategy

                        After keypoints have been extracted from the hint image and
                        candidate images, we need to evaluate which of the candidates is most likely.

                        For a hint image, the corresponding source image would contain keypoints with:
                        - similar characteristics (scale, orientation)
                        - similar relative positioning

                        In other words there should be pairs or even groups of keypoints
                        that form "fingerprints" which appear in both hint and source images. It is insufficient to match using individual keypoints because their absolute position information is useless due to the hint being a crop
                        of unknown position.

                        My strategy is to consider pairs of keypoints and for each pair compute distance and angle
                        between them. The pairs are limited to the k-nearest neighbours of each keypoint. I've set
                        k to 5 somewhat randomly and have not bothered to tune any further.

                        This information is concatenated into a string, along with the orientation and scale of both keypoints.
                        A small degree of quantisation is applied to handle imprecision or variabilty in the keypoint values.

                        Identifying the most likely source image then consists of finding the source image with the largest number
                        of the same strings. The figure below shows that 84 matches were found between the Wonka hint image and frame 18
                        in the candidate set, which is the correct source, while other images have zero matches.
                    """
                    ),
                    html.Img(
                        src="/assets/frame18_hist.png",
                        style={"width": "100%"},
                        className="mb-3",
                    ),
                    dcc.Markdown(
                        """
                        ## Limitations

                        The main limitations of this implementation is that
                        I am only finding matches within the frames already used. A real implementation
                        would need to index every frame of films, tv etc, which is a costly and time consuming endeavour.

                        ## Practical Considerations

                        - Use SURF instead of SIFT features to gain rotation invariance.
                        - Incorporate colour based features, for low contrast images e.g. frame 2 from Moana and frame 14 from Sicario.
                        - We know that Siracusa is most likely to only include frames from visual media
                        that he has watched. Therefore it would be prudent to first search his [Letterboxd profile](https://letterboxd.com/siracusa/).

                        ## Broader Improvements

                        - The scoring strategy could be improved. Instead of checking for matches
                        against single frames, the number of matches across a source video could be used.
                        This is similar to Shazam's scoring strategy.

                        ## Code

                        Complete code is available in this [Github](http://github.com/sjtrny/framegame) repo.

                        ## About Me

                        Read more about me here https://sjtrny.com
                    """
                    ),
                ],
                width=7,
            )
        ),
    ],
    className="mb-5 mt-3",
)
