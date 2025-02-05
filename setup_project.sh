echo "Installing dependencies..."
# generate keys

python utils/keys_manager.py

# install packages
cd frontend || exit
npm install
echo "Finished installing dependencies!"