#include <chrono>
#include <iostream>
#include <string>
#include <vector>

#include <cpr/cpr.h>
#include <nlohmann/json.hpp>

#include <Eigen/Dense>

// --------------------
// Timing helper
// --------------------
struct Timer {
  using clock = std::chrono::high_resolution_clock;
  clock::time_point t0;
  Timer() : t0(clock::now()) {}
  double ms() const {
    auto t1 = clock::now();
    return std::chrono::duration<double, std::milli>(t1 - t0).count();
  }
};

// --------------------
// Convert JSON arrays to Eigen
// --------------------
static Eigen::MatrixXd json_to_mat(const nlohmann::json &a) {
  const auto rows = a.size();
  const auto cols = rows ? a[0].size() : 0;
  Eigen::MatrixXd A(rows, cols);
  for (size_t i = 0; i < rows; ++i) {
    for (size_t j = 0; j < cols; ++j) {
      A(static_cast<Eigen::Index>(i), static_cast<Eigen::Index>(j)) =
          a[i][j].get<double>();
    }
  }
  return A;
}

static Eigen::VectorXd json_to_vec(const nlohmann::json &v) {
  const auto n = v.size();
  Eigen::VectorXd b(n);
  for (size_t i = 0; i < n; ++i) {
    b(static_cast<Eigen::Index>(i)) = v[i].get<double>();
  }
  return b;
}

static nlohmann::json vec_to_json(const Eigen::VectorXd &x) {
  nlohmann::json j = nlohmann::json::array();
  for (Eigen::Index i = 0; i < x.size(); ++i) {
    j.push_back(x(i));
  }
  return j;
}

int main(int argc, char **argv) {
  std::string base_url = "http://127.0.0.1:8000";
  if (argc >= 2)
    base_url = argv[1];

  // Optionnel: afficher nb threads Eigen (peut être >1 si OpenMP actif)
  // Eigen::setNbThreads(4);

  std::cout << "Connecting to proxy at: " << base_url << "\n";
  std::cout << "Press Ctrl+C to stop.\n\n";

  while (true) {
    // 1) GET a task
    Timer t_get;
    auto r = cpr::Get(cpr::Url{base_url},
                      cpr::Header{{"Accept", "application/json"}},
                      cpr::Timeout{30000});
    const double get_ms = t_get.ms();

    if (r.error) {
      std::cerr << "GET error: " << r.error.message << "\n";
      return 1;
    }
    if (r.status_code != 200) {
      std::cerr << "GET status: " << r.status_code << "\n";
      std::cerr << r.text << "\n";
      return 1;
    }

    // 2) Parse JSON
    Timer t_parse;
    nlohmann::json task_json = nlohmann::json::parse(r.text);
    const double parse_ms = t_parse.ms();

    // Expected fields from Python: identifier, size, a, b, x, time
    const int identifier = task_json.at("identifier").get<int>();
    // size can be large, but is redundant if a/b provided:
    // const int size = task_json.at("size").get<int>();

    // 3) Build Eigen objects
    Timer t_build;
    Eigen::MatrixXd A = json_to_mat(task_json.at("a"));
    Eigen::VectorXd b = json_to_vec(task_json.at("b"));
    const double build_ms = t_build.ms();

    // 4) Solve A x = b
    Timer t_solve;
    // Robust solve (similar to numpy.linalg.solve):
    Eigen::VectorXd x = A.partialPivLu().solve(b);
    const double solve_ms = t_solve.ms();

    // (Optionnel) check residual quickly
    const double residual = (A * x - b).norm();

    // 5) Prepare result JSON (update x and time)
    Timer t_dump;
    task_json["x"] = vec_to_json(x);
    task_json["time"] =
        solve_ms / 1000.0; // seconds, comme en Python (perf_counter delta)
    // keep identifier/size/a/b as-is (proxy expects Task.from_json)
    const std::string out = task_json.dump();
    const double dump_ms = t_dump.ms();

    // 6) POST back
    Timer t_post;
    auto p = cpr::Post(cpr::Url{base_url},
                       cpr::Header{{"Content-Type", "application/json"}},
                       cpr::Body{out}, cpr::Timeout{30000});
    const double post_ms = t_post.ms();

    if (p.error) {
      std::cerr << "POST error: " << p.error.message << "\n";
      return 1;
    }
    if (p.status_code != 200) {
      std::cerr << "POST status: " << p.status_code << "\n";
      std::cerr << p.text << "\n";
      return 1;
    }

    // Summary line
    std::cout << "Task " << identifier << " | GET " << get_ms << " ms"
              << " | parse " << parse_ms << " ms"
              << " | build " << build_ms << " ms"
              << " | solve " << solve_ms << " ms"
              << " | dump " << dump_ms << " ms"
              << " | POST " << post_ms << " ms"
              << " | residual " << residual << "\n";
  }

  return 0;
}
