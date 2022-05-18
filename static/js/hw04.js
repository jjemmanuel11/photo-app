const modalElement = document.querySelector('.modal-bg');
modalFocusClose = document.querySelector('.profile_follow button');
// --------------------POSTS--------------------
const displayPosts = () => {
    fetch('/api/posts')
        .then(response => response.json())
        .then(posts => {
            limited_posts = posts.slice(0,10);
            const html = limited_posts.map(post2Html).join('\n');
            document.querySelector('#posts').innerHTML = html;
        })
};

const post2Html = post => {
    return `<section class="post">${post2HtmlHelper(post)}</section>`;
};

const post2HtmlHelper = (post) => {
    // likes
    const likes_num = post.likes.length;
    likes_text = 'like';
    if (likes_num !=1) {
        likes_text = likes_text + "s";
    }
    // like icon
    if (post.current_user_like_id) {
        like_icon = `<button
            aria-label="Like"
            aria-checked="true"
            onClick = toggleLike(event)
            data-post-id = ${post.id}
            data-like-id = ${post.current_user_like_id}
            class = "Liked"><i class="fas fa-heart fa-lg"></i></button>`;
    }
    else {
        like_icon = `<button
            aria-label="Like"
            aria-checked="false"
            onClick = toggleLike(event)
            data-post-id = ${post.id}><i class="far fa-heart fa-lg"></i></button>`;
    }
    // bookmark icon
    if (post.current_user_bookmark_id) {
        bookmark_icon = `<button
            aria-label="Bookmark"
            aria-checked="true"
            onClick = toggleBookmark(event)
            data-post-id = ${post.id}
            data-bookmark-id = ${post.current_user_bookmark_id}
            class = "Bookmarked"><i class="fas fa-bookmark fa-lg"></i></button>`;
    }
    else {
        bookmark_icon = `<button
            aria-label="Bookmark"
            aria-checked="false"
            onClick = toggleBookmark(event)
            data-post-id = ${post.id}><i class="far fa-bookmark fa-lg"></i></button>`;
    }
    
    // display time
    const display_time = post.display_time.toUpperCase();
    // comments
    const comment_num = post.comments.length;
    
    if (comment_num > 2) {
        display_comments = `<button
                onClick= openModal(event,${post.id})
                class="blue view_comments">View all ${comment_num-1} comments</button>`;
        last_comment = post.comments[comment_num-1];
    }
    else if (comment_num > 1) {
        display_comments = `<button
                onClick= openModal(event,${post.id})
                class="blue view_comments">View all 1 comment</button>`;
        last_comment = post.comments[comment_num-1];
    }
    else {
        display_comments = ``;
    }
    // caption
    if (post.caption.length > 90) {
        shorter_caption = post.caption.substr(0,90);
        edited_caption =
        `<p>
            <span class="bolded">${post.user.username}</span>
            ${shorter_caption}...
            <span class="blue">more</span>
        </p>`;
    }
    else {
        edited_caption =
        `<p>
            <span class="bolded">${post.user.username}</span>
            ${post.caption}
        </p>`;
    }
    // return
    return `
        <section class="header">
            <h2>${post.user.username}</h2>            
            <i class="fas fa-ellipsis-h"></i>
        </section>
    
        <img src="${post.image_url}" alt="${post.user.username} post picture">

        <section class="comments_description">
            <section class="react">
                <section>
                    ${like_icon}
                    <button onClick= openModal(event,${post.id})><i class="far fa-comment fa-lg"></i></button>
                    <button><i class="far fa-paper-plane fa-lg"></i></button>
                </section>
                ${bookmark_icon}
            </section>
            <p class="likes">${likes_num} ${likes_text}</p>
            
            <section class="caption">
                ${edited_caption}
            </section>

            <section class="comments">
                ${display_comments}
                    <p class="comment">
                        <span class="bolded">${last_comment.user.username}</span>
                        ${last_comment.text}
                    </p>
                <p class="grey">${display_time}</p>
            </section>
        </section>

        <section class="add_comment">
            <section>
                <i class="far fa-smile fa-lg"></i>
                <textarea
                    type="text"
                    rows="1"
                    data-post-id = ${post.id}
                    placeholder="Add a comment..."></textarea>
            </section>
            <button class="blue"
                    onClick = createNewComment(event,${post.id})
                    data-post-id = ${post.id}>Post</button>
        </section>
    `;
};
// --------------------MODAL--------------------
const openModal = async(event,postId) => {
    modalFocusClose = await event.currentTarget;
    html = ``;
    await fetch(`/api/posts/${postId}`, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        html = post2Modal(data);
        console.log(html);
    });
    modalElement.querySelector('.modal-body').innerHTML= html;
    modalElement.classList.remove('hidden');
    modalElement.setAttribute('aria-hidden', 'false');
    document.querySelector('.close').focus();
    
}

const closeModal = (event) => {
    modalElement.classList.add('hidden');
    modalElement.setAttribute('aria-hidden', 'true');
    modalFocusClose.focus();
};

const post2Modal = (post) => {
    const caption_html = `<section class="modal-comment">
                            <img src="${post.user.thumb_url}" alt="${post.user.username} post picture">
                            <section>
                                <p><span class="bolded">${post.user.username}</span>
                                    ${post.caption}
                                </p>
                                <p>${post.display_time}</p>
                            </section>
                            <button><i class="far fa-heart fa-lg"></i></button>
                        </section>`;
    const comment_html = post.comments.map(comment2Html).join('\n');
    return `
        <section>
            <img src="${post.image_url}" alt="${post.user.username} post picture">
        </section>
        <section id="modal-panel">
            <section id="modal-profile">
                <img src="${post.user.thumb_url}" alt="${post.user.username} profile picture">
                <h2>${post.user.username}</h2>
            </section>
            <section id="modal-comments">
                ${caption_html}
                ${comment_html}
                <section id="modal-spacing"></section>
            </section>
        </section>
    `;
    //text
    //text
    //days ago
    //heart
};


const comment2Html = (comment) => {
    return `<section class="modal-comment">
                <img src="${comment.user.thumb_url}" alt="${comment.user.username} post picture">
                <section>
                    <p><span class="bolded">${comment.user.username}</span>
                        ${comment.text}
                    </p>
                    <p>${comment.display_time}</p>
                    
                </section>
                <button><i class="far fa-heart fa-lg"></i></button>
            </section>`;
};

document.addEventListener('keydown', function(event){
	if(event.key === "Escape" && !modalElement.classList.contains('hidden')){
		closeModal(event);
	}
});

// --------------------COMMENTS--------------------
const createNewComment = async(event,postId) => {
    const elem = event.currentTarget;
    const comment = elem.parentNode.querySelector('textarea');
    const postData = {
        "post_id": postId,
        "text": comment.value
    };
    
    await fetch("/api/comments", {
        method: "POST",
        headers: {
            'content-type': "application/json"
        },
        body: JSON.stringify(postData)
    }).then(response => response.json())
    .then(data => {
        comment.value="";
    });
    post_elem = await elem.parentNode.parentNode;
    post_elem.innerHTML = await getPost(postId);
    const comment_box = post_elem.querySelector('textarea');
    await comment_box.focus();
    await comment_box.select();
};

document.addEventListener('focus', function(event) {
    if (modalElement.getAttribute('aria-hidden') === 'false' && !modalElement.contains(event.target)) {
        event.stopPropagation();
        document.querySelector('.close').focus();
    }
}, true);

// --------------------LIKES--------------------
const toggleLike =async(event)=> {
    const elem = event.currentTarget;
    const postId = elem.dataset.postId;
    if (await elem.classList.contains("Liked")) {
        await deleteLike(elem.dataset.likeId,elem);
    }
    else {
        await createNewLike(postId,elem);
    }
    post_elem = await elem.parentNode.parentNode.parentNode.parentNode;
    post_elem.innerHTML = await getPost(postId);
};

const createNewLike = async(postId,elem) => {
    const postData = {
        "post_id": postId
    };
    await fetch("/api/posts/likes", {
        method: "POST",
        headers: {
            'content-type': "application/json"
        },
        body: JSON.stringify(postData)
    })
};

const deleteLike = async(likeId,elem)=> {
    const deleteURL = `/api/posts/likes/${likeId}`;
    await fetch(deleteURL, {
        method: "DELETE",
        headers: {
            'Content-Type': 'application/json',
        }
    })
};

const getPost = async(postId) => {
    const reloadURL = `/api/posts/${postId}`;
    html = ``;
    await fetch(reloadURL, {
        method: "GET",
        headers: {
            'content-type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        html= post2HtmlHelper(data);
    });
    return html;
};

// --------------------BOOKMARKS--------------------
const toggleBookmark =async(event)=> {
    const elem = event.currentTarget;
    const postId = elem.dataset.postId;
    if (await elem.classList.contains("Bookmarked")) {
        await deleteBookmark(elem.dataset.bookmarkId,elem);
    }
    else {
        await createNewBookmark(postId,elem);
    }
};

const createNewBookmark = async(postId,elem) => {
    const postData = {
        "post_id": postId
    };
    await fetch("/api/bookmarks", {
        method: "POST",
        headers: {
            'content-type': "application/json"
        },
        body: JSON.stringify(postData)
    }).then(response => response.json())
    .then(data => {
        elem.innerHTML = `<i class="fas fa-bookmark fa-lg"></i>`;
        elem.classList.add("Bookmarked");
        elem.setAttribute("aria-checked","true");
        elem.setAttribute("data-bookmark-id",data.id);
    });
};

const deleteBookmark = async(likeId,elem)=> {
    const deleteURL = `/api/bookmarks/${likeId}`;
    await fetch(deleteURL, {
        method: "DELETE",
        headers: {
            'Content-Type': 'application/json',
        }
    }).then(response => response.json())
    .then(data => {
        elem.innerHTML = `<i class="far fa-bookmark fa-lg"></i>`;
        elem.classList.remove("Bookmarked");
        elem.setAttribute("aria-checked","false");
        elem.removeAttribute("data-bookmark-id",data.id);
    });
};

// --------------------STORIES--------------------
// fetch data from your API endpoint:
const displayStories = () => {
    fetch('/api/stories')
        .then(response => response.json())
        .then(stories => {
            const html = stories.map(story2Html).join('\n');
            document.querySelector('#stories').innerHTML = html;
        })
};

const story2Html = story => {
    return `
        <section>
            <img src="${ story.user.thumb_url }" class="pic" alt="profile pic for ${ story.user.username }" />
            <p>${ story.user.username }</p>
        </section>
    `;
};

// --------------------SUGGESTIONS--------------------
const displaySuggestions = () => {
    fetch('/api/suggestions')
        .then(response => response.json())
        .then(users => {
            const html2 = users.map(user2Html).join('\n');
            document.querySelector('#other_profiles').innerHTML = html2;
        })

};

const user2Html = user => {
    return `<section class="profile_follow">
                <img src="${user.thumb_url}" alt="profile picture for ${user.username}">
                <section>
                    <p class="username">${user.username}</p>
                    <p class="grey">Suggested for you</p>
                </section>
                <button
                    aria-label="Follow"
                    aria-checked="false"
                    class="Follow blue"
                    onClick = toggleFollow(event)
                    data-user-id = ${user.id}
                >Follow</button>
            </section>`
            
};
// --------------------FOLLOWS--------------------
const toggleFollow = event => {
    const elem = event.currentTarget;
    const userId = elem.dataset.userId;

    if (elem.innerHTML === "Follow") {
        createNewFollow(userId,elem);
    }
    else {
        deleteFollower(elem.dataset.followingId,elem);
    }
};

const createNewFollow = (userId,elem) => {
    const postData = {
        "user_id": userId
    };
    fetch("/api/following", {
        method: "POST",
        headers: {
            'content-type': "application/json"
        },
        body: JSON.stringify(postData)
    })
    .then(response => response.json())
    .then(data => {
        elem.innerHTML = "Unfollow";
        elem.classList.add("Unfollow");
        elem.classList.remove("Follow");
        elem.setAttribute("aria-checked","true");
        elem.setAttribute("data-following-id",data.id);
    })
};

const deleteFollower = (followerID,elem)=> {
    const deleteURL = `/api/following/${followerID}`;
    fetch(deleteURL, {
        method: "DELETE",
    })
    .then(response => response.json())
    .then(data => {
        elem.innerHTML = "Follow";
        elem.classList.add("Follow");
        elem.classList.remove("Unfollow");
        elem.setAttribute("aria-checked","false");
        elem.removeAttribute("data-following-id",data.id);
    })
};

// --------------------GENERAL--------------------

const initPage = () => {
    displayStories();
    displaySuggestions();
    displayPosts();
};

// invoke init page to display stories:
initPage();

