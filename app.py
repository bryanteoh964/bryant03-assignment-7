from flask import Flask, render_template, request, url_for, session
import numpy as np
import matplotlib
from scipy.stats import norm

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Replace with your own secret key, needed for session management


def generate_data(N, mu, beta0, beta1, sigma2, S):
    # Generate data and initial plots

    # TODO 1: Generate a random dataset X of size   N with values between 0 and 1
    X = np.random.uniform(0, 1, N)  
    X = X.reshape(-1, 1)

    # TODO 2: Generate a random dataset Y using the specified beta0, beta1, mu, and sigma2
    # Y = beta0 + beta1 * X + mu + error term
    Y = beta0 + beta1 * X + np.random.normal(mu, np.sqrt(sigma2), N).reshape(-1, 1)

    # TODO 3: Fit a linear regression model to X and Y
    model = LinearRegression()  # Initialize model
    model.fit(X, Y)  # Replace with code to fit the model
    slope = model.coef_[0][0]  # Replace with code to extract slope from the fitted model
    intercept = model.intercept_[0]  # Replace with code to extract intercept from the fitted model
    print("Slope:", slope, "Type", type(slope))
    print("Intercept:", intercept, "Type", type(intercept))

    # TODO 4: Generate a scatter plot of (X, Y) with the fitted regression line
    plt.figure(figsize=(10, 5))
    plt.scatter(X, Y, color="blue", label="Data")
    plt.plot(X, model.predict(X), color="red", label=f"Y = {slope}X + {intercept}")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title(f"Linear Regression: Y = {slope}X + {intercept}")
    plt.legend()
    plt.tight_layout()
    plot1_path = "static/plot1.png"
    plt.savefig(plot1_path)

    # TODO 5: Run S simulations to generate slopes and intercepts
    slopes = []
    intercepts = []

    for _ in range(S):
        # TODO 6: Generate simulated datasets using the same beta0 and beta1
        X_sim = np.random.uniform(0, 1, N).reshape(-1, 1)  # Replace with code to generate simulated X values
        Y_sim = beta0 + beta1 * X + np.random.normal(mu, np.sqrt(sigma2), N).reshape(-1, 1)  # Replace with code to generate simulated Y values

        # TODO 7: Fit linear regression to simulated data and store slope and intercept
        sim_model = LinearRegression()
        sim_model.fit(X_sim, Y_sim)
        # Extract slope from sim_model
        # Extract intercept from sim_model
        sim_slope = sim_model.coef_[0][0]
        sim_intercept = sim_model.intercept_[0]

        slopes.append(sim_slope)
        intercepts.append(sim_intercept)

    # TODO 8: Plot histograms of slopes and intercepts
    plt.figure(figsize=(10, 5))
    plt.hist(slopes, bins=20, alpha=0.5, color="blue", label="Slopes")
    plt.hist(intercepts, bins=20, alpha=0.5, color="orange", label="Intercepts")
    plt.axvline(slope, color="blue", linestyle="--", linewidth=1, label=f"Slope: {slope}")
    plt.axvline(intercept, color="orange", linestyle="--", linewidth=1, label=f"Intercept: {intercept}")
    plt.title("Histogram of Slopes and Intercepts")
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.legend()
    plot2_path = "static/plot2.png"
    plt.savefig(plot2_path)
    plt.close()

    # TODO 9: Return data needed for further analysis, including slopes and intercepts
    # Calculate proportions of slopes and intercepts more extreme than observed
    slope_more_extreme = sum(s > slope for s in slopes) / S  # Replace with code to calculate proportion of slopes more extreme than observed
    intercept_extreme = sum(i < intercept for i in intercepts) / S   # Replace with code to calculate proportion of intercepts more extreme than observed

    # Return data needed for further analysis
    return (
        X,
        Y,
        slope,
        intercept,
        plot1_path,
        plot2_path,
        slope_more_extreme,
        intercept_extreme,
        slopes,
        intercepts,
    )


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get user input from the form
        N = int(request.form["N"])
        mu = float(request.form["mu"])
        sigma2 = float(request.form["sigma2"])
        beta0 = float(request.form["beta0"])
        beta1 = float(request.form["beta1"])
        S = int(request.form["S"])

        # Generate data and initial plots
        (
            X,
            Y,
            slope,
            intercept,
            plot1,
            plot2,
            slope_extreme,
            intercept_extreme,
            slopes,
            intercepts,
        ) = generate_data(N, mu, beta0, beta1, sigma2, S)

        # Store data in session
        session["X"] = X.tolist()
        session["Y"] = Y.tolist()
        session["slope"] = slope
        session["intercept"] = intercept
        session["slopes"] = slopes
        session["intercepts"] = intercepts
        session["slope_extreme"] = slope_extreme
        session["intercept_extreme"] = intercept_extreme
        session["N"] = N
        session["mu"] = mu
        session["sigma2"] = sigma2
        session["beta0"] = beta0
        session["beta1"] = beta1
        session["S"] = S

        print("Session data after setting:", session)  # Debugging output
        # print session byte size
        print("Session byte size:", len(str(session)))
        session.modified = True

        # Return render_template with variables
        return render_template(
            "index.html",
            plot1=plot1,
            plot2=plot2,
            slope_extreme=slope_extreme,
            intercept_extreme=intercept_extreme,
            N=N,
            mu=mu,
            sigma2=sigma2,
            beta0=beta0,
            beta1=beta1,
            S=S,
        )
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    # This route handles data generation (same as above)
    try:
        N = int(request.form.get('N'))
        mu = float(request.form.get('mu'))
        sigma2 = float(request.form.get('sigma2'))
        beta0 = float(request.form.get('beta0'))
        beta1 = float(request.form.get('beta1'))
        S = int(request.form.get('S'))
        print(f"Received parameters - N: {N}, mu: {mu}, sigma2: {sigma2}, beta0: {beta0}, beta1: {beta1}, S: {S}")
    except TypeError as e:
        print("Error:", e)
    return index()


@app.route("/hypothesis_test", methods=["POST"])
def hypothesis_test():
    try:
        print("trying to get session!!!")
        print("Session data", session)
        N = session.get("N")
        print("session is", N)
    except:
        print("Session not found.")
    N = int(session.get("N"))
    S = int(session.get("S"))
    slope = float(session.get("slope"))
    intercept = float(session.get("intercept"))
    slopes = session.get("slopes")
    intercepts = session.get("intercepts")
    beta0 = float(session.get("beta0"))
    beta1 = float(session.get("beta1"))

    parameter = request.form.get("parameter")
    test_type = request.form.get("test_type")

    # Use the slopes or intercepts from the simulations
    if parameter == "slope":
        simulated_stats = np.array(slopes)
        observed_stat = slope
        hypothesized_value = beta1
    else:
        simulated_stats = np.array(intercepts)
        observed_stat = intercept
        hypothesized_value = beta0

    # TODO 10: Calculate p-value based on test type
    p_value = None
    if test_type == "two-sided":
        p_value = np.mean(np.abs(simulated_stats - hypothesized_value) >= np.abs(observed_stat - hypothesized_value))
    else:
        if observed_stat > hypothesized_value:
            p_value = np.mean(simulated_stats >= observed_stat)
        else:
            p_value = np.mean(simulated_stats <= observed_stat)

    # TODO 11: If p_value is very small (e.g., <= 0.0001), set fun_message to a fun message
    fun_message = None
    if p_value <= 0.0001:
        fun_message = "Wow, that's highly significant!"

    # TODO 12: Plot histogram of simulated statistics
    plt.figure(figsize=(10, 5))
    plt.hist(simulated_stats, bins=20, alpha=0.5, color="skyblue", label="Simulated values")
    plt.axvline(observed_stat, color="red", linestyle="--", label=f"Observed {parameter}: {observed_stat:.2f}")
    plt.axvline(hypothesized_value, color="green", linestyle="--", label=f"Hypothesized {parameter}: {hypothesized_value:.2f}")
    plt.title(f"Distribution of Simulated {parameter.capitalize()} Values")
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.savefig("static/plot3.png")
    plt.close()

    # Return results to template
    return render_template(
        "index.html",
        plot1="static/plot1.png",
        plot2="static/plot2.png",
        plot3="static/plot3.png",
        parameter=parameter,
        observed_stat=observed_stat,
        hypothesized_value=hypothesized_value,
        N=N,
        beta0=beta0,
        beta1=beta1,
        S=S,
        # TODO 13: Uncomment the following lines when implemented
        p_value=p_value,
        fun_message=fun_message,
    )

@app.route("/confidence_interval", methods=["POST"])
def confidence_interval():
    # Retrieve data from session
    N = int(session.get("N"))
    mu = float(session.get("mu"))
    sigma2 = float(session.get("sigma2"))
    beta0 = float(session.get("beta0"))
    beta1 = float(session.get("beta1"))
    S = int(session.get("S"))
    X = np.array(session.get("X"))
    Y = np.array(session.get("Y"))
    slope = float(session.get("slope"))
    intercept = float(session.get("intercept"))
    slopes = session.get("slopes")
    intercepts = session.get("intercepts")

    parameter = request.form.get("parameter")
    confidence_level = float(request.form.get("confidence_level"))
    if confidence_level > 1:
        confidence_level /= 100

    # Use the slopes or intercepts from the simulations
    if parameter == "slope":
        estimates = np.array(slopes)
        observed_stat = slope
        true_param = beta1
    else:
        estimates = np.array(intercepts)
        observed_stat = intercept
        true_param = beta0

    # TODO 14: Calculate mean and standard deviation of the estimates
    mean_estimate = np.mean(estimates)
    std_estimate = np.std(estimates)

    # TODO 15: Calculate confidence interval for the parameter estimate
    # Use the t-distribution and confidence_level
    # import to use norm.ppf
    from scipy.stats import norm
    # e.g., z_score ≈ 1.96 for 95% confidence
    z_score = norm.ppf(1 - (1 - confidence_level) / 2)
    print("z_score:", z_score)
    ci_lower = mean_estimate - z_score * std_estimate
    ci_upper = mean_estimate + z_score * std_estimate

    # TODO 16: Check if confidence interval includes true parameter
    includes_true = ci_lower <= true_param <= ci_upper

    # chack important values:
    print("------------------------------------")
    print("parameter:", parameter)
    print("confidence_level:", confidence_level)
    print("mean_estimate:", mean_estimate)
    print("std_estimate:", std_estimate)
    print("z_score:", z_score)
    print("ci_lower:", ci_lower)
    print("ci_upper:", ci_upper)
    print("includes_true:", includes_true)
    print("------------------------------------")

    # TODO 17: Plot the individual estimates as gray points and confidence interval
    # Plot the mean estimate as a colored point which changes if the true parameter is included
    # Plot the confidence interval as a horizontal line
    # Plot the true parameter value
    plt.figure(figsize=(10, 5))
    plt.plot(estimates, 'o', color='gray', alpha=0.5, label="Individual Estimates")
    plt.axhline(true_param, color="blue", linestyle="--", label=f"True {parameter.capitalize()}: {true_param:.2f}")
    plt.axhline(mean_estimate, color="orange", label=f"Mean Estimate: {mean_estimate:.2f}")
    plt.fill_between(range(len(estimates)), ci_lower, ci_upper, color="yellow", alpha=0.3, label="Confidence Interval")
    plt.title(f"Confidence Interval for {parameter.capitalize()}")
    plt.xlabel("Simulation Index")
    plt.ylabel("Estimate Value")
    plt.legend()
    plt.tight_layout()
    plt.savefig("static/plot4.png")
    plt.close()

    # Return results to template
    return render_template(
        "index.html",
        plot1="static/plot1.png",
        plot2="static/plot2.png",
        plot4="static/plot4.png",
        parameter=parameter,
        confidence_level=int(confidence_level*100),
        mean_estimate=mean_estimate,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        includes_true=includes_true,
        observed_stat=observed_stat,
        N=N,
        mu=mu,
        sigma2=sigma2,
        beta0=beta0,
        beta1=beta1,
        S=S,
    )


if __name__ == "__main__":
    app.run(debug=True)
