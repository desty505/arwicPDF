import pkg_resources

# インストールされている全てのパッケージを取得
installed_packages = pkg_resources.working_set

print("Installed packages:")
for package in installed_packages:
    print(f"{package.key}=={package.version}")
