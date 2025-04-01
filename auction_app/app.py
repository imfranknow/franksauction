from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'hfuehuiwehwer498rh4rdsjdb32eghj32'  # Replace with a strong secret key

# Auction item details defined in code
auction_item = "Magic Snowflake"
auction_image = "/static/uploads/snowflake.png"  # Ensure this image exists in the static/uploads folder

# Auction state variables
highest_bid = 0
highest_bidder = None
auction_end_time = None  # Will be set when the first bid is placed

# Store all bids in a list. Each bid is a dictionary with amount, bidder, and time.
bids = []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            session['username'] = username
            return redirect(url_for('auction'))
        else:
            flash("Please enter a username")
    return render_template('index.html')

@app.route('/auction', methods=['GET', 'POST'])
def auction():
    global highest_bid, highest_bidder, auction_end_time, bids
    if 'username' not in session:
        return redirect(url_for('index'))
    
    now = datetime.now()
    auction_ended = False
    remaining_time = None

    # Compute remaining time if auction has started
    if auction_end_time:
        if now > auction_end_time:
            auction_ended = True
            remaining_time = "00:00:00"
        else:
            remaining_delta = auction_end_time - now
            hours, remainder = divmod(remaining_delta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            remaining_time = f"{hours:02}:{minutes:02}:{seconds:02}"

    if request.method == 'POST':
        # Reject bids if the auction has ended
        if auction_end_time and now > auction_end_time:
            flash("Auction has ended. No more bids accepted.")
            return redirect(url_for('auction'))

        bid = request.form.get('bid')
        try:
            bid = int(bid)
            if bid > highest_bid:
                highest_bid = bid
                highest_bidder = session['username']
                # Record the bid along with bidder and timestamp
                bids.append({
                    "bid": bid,
                    "bidder": session['username'],
                    "time": now.strftime("%Y-%m-%d %H:%M:%S")
                })
                # Start the 1‑hour timer when the first bid is placed
                if auction_end_time is None:
                    auction_end_time = now + timedelta(hours=1)
                # Apply the sniper rule: if less than 30 seconds remain, extend the auction
                elif (auction_end_time - now).total_seconds() < 30:
                    auction_end_time = now + timedelta(seconds=30)
                flash("Your bid has been placed!")
            else:
                flash("Your bid must be higher than the current highest bid.")
        except ValueError:
            flash("Please enter a valid number.")
        return redirect(url_for('auction'))

    return render_template('auction.html', 
                           auction_item=auction_item, 
                           auction_image=auction_image,
                           highest_bid=highest_bid, 
                           highest_bidder=highest_bidder,
                           auction_ended=auction_ended,
                           remaining_time=remaining_time,
                           auction_end_time=auction_end_time,
                           bids=bids)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

